from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, field_validator
from typing import List, Optional
import data_store
from utils.id_generator import next_counter_id, get_reusable_ids, get_next_id_preview, sync_counter

router = APIRouter()


class KeyResult(BaseModel):
    id: str
    name: str


class Objective(BaseModel):
    id: str
    name: str
    tech_stack: str = ""
    key_results: List[KeyResult] = []
    status: str = "진행중"


class ObjectiveUpdate(BaseModel):
    name: Optional[str] = None
    tech_stack: Optional[str] = None
    key_results: Optional[List[KeyResult]] = None
    status: Optional[str] = None


class KeyResultCreate(BaseModel):
    name: str


def _load() -> list:
    data = data_store.load("okrs.json")
    return data.get("objectives", [])


def _save(objectives: list) -> None:
    data_store.save("okrs.json", {"objectives": objectives})


def _get_next_key_result_id(objective: dict) -> str:
    key_results = objective.get("key_results", [])
    max_num = 0
    for kr in key_results:
        try:
            num = int(kr["id"].replace("KR", ""))
            if num > max_num:
                max_num = num
        except (ValueError, KeyError):
            pass
    return f"KR{max_num + 1}"


def _calculate_progress(objective: dict) -> int:
    key_results = objective.get("key_results", [])
    if not key_results:
        return 0
    return 100 // len(key_results) if key_results else 0


# ── Objective endpoints ────────────────────────────────────────────────────────

@router.get("", response_model=List[Objective])
def list_objectives():
    return _load()


@router.get("/next-id")
def get_next_id():
    objectives = _load()
    return {"next_id": get_next_id_preview("O", objectives)}


@router.get("/reusable-ids")
def get_reusable_objective_ids():
    objectives = _load()
    return {"reusable_ids": get_reusable_ids(objectives, "O")}


@router.get("/{objective_id}", response_model=Objective)
def get_objective(objective_id: str):
    objectives = _load()
    for o in objectives:
        if o["id"] == objective_id:
            return o
    raise HTTPException(status_code=404, detail="Objective not found")


@router.post("", response_model=Objective, status_code=201)
def create_objective(objective: Objective):
    objectives = _load()
    if not objective.id:
        objective.id = next_counter_id("O", objectives)
    else:
        # 사용자가 직접 입력한 ID → 카운터가 이 값보다 낮으면 카운터도 갱신
        sync_counter("O", objective.id, objectives)
    if any(o["id"] == objective.id for o in objectives):
        raise HTTPException(status_code=400, detail="Objective id already exists")
    objectives.append(objective.model_dump())
    _save(objectives)
    return objective



@router.put("/{objective_id}", response_model=Objective)
def update_objective(objective_id: str, update: ObjectiveUpdate):
    objectives = _load()
    for i, o in enumerate(objectives):
        if o["id"] == objective_id:
            patch = update.model_dump(exclude_none=True)
            objectives[i] = {**o, **patch}
            _save(objectives)
            return objectives[i]
    raise HTTPException(status_code=404, detail="Objective not found")


@router.delete("/{objective_id}")
def delete_objective(objective_id: str):
    objectives = _load()
    objective = next((o for o in objectives if o["id"] == objective_id), None)
    if not objective:
        raise HTTPException(status_code=404, detail="Objective not found")

    objective_name = objective["name"]

    # Cascade: tasks.objective_id 초기화
    tasks_data = data_store.load("tasks.json")
    tasks_changed = False
    for task in tasks_data.get("tasks", []):
        if task.get("objective_id") == objective_id:
            task["objective_id"] = ""
            tasks_changed = True
    if tasks_changed:
        data_store.save("tasks.json", tasks_data)

    # Cascade: staff.okrs에서 제거
    staff_data = data_store.load("staff.json")
    staff_changed = False
    for staff in staff_data.get("staff", []):
        okrs_str = staff.get("okrs", "")
        if okrs_str:
            ids = [x.strip() for x in okrs_str.split(",") if x.strip()]
            new_ids = [x for x in ids if x != objective_id]
            if len(new_ids) != len(ids):
                staff["okrs"] = ",".join(new_ids)
                staff_changed = True
    if staff_changed:
        data_store.save("staff.json", staff_data)

    # Cascade: progress의 objective ID를 이름 텍스트로 변환 (이력 보존)
    progress_data = data_store.load("progress.json")
    progress_changed = False
    for item in progress_data.get("progress_items", []):
        if item.get("objective") == objective_id:
            item["objective"] = objective_name
            progress_changed = True
    if progress_changed:
        data_store.save("progress.json", progress_data)

    new_objectives = [o for o in objectives if o["id"] != objective_id]
    _save(new_objectives)
    return {"deleted": objective_id}


# ── Key Result endpoints ───────────────────────────────────────────────────────

@router.post("/{objective_id}/key-results", response_model=KeyResult, status_code=201)
def add_key_result(objective_id: str, key_result: KeyResultCreate):
    objectives = _load()
    for o in objectives:
        if o["id"] == objective_id:
            kr_id = _get_next_key_result_id(o)
            new_kr = {"id": kr_id, "name": key_result.name}
            o.setdefault("key_results", []).append(new_kr)
            _save(objectives)
            return new_kr
    raise HTTPException(status_code=404, detail="Objective not found")


@router.put("/{objective_id}/key-results/{kr_id}", response_model=KeyResult)
def update_key_result(objective_id: str, kr_id: str, update: KeyResultCreate):
    objectives = _load()
    for o in objectives:
        if o["id"] == objective_id:
            for i, kr in enumerate(o.get("key_results", [])):
                if kr["id"] == kr_id:
                    o["key_results"][i] = {"id": kr_id, "name": update.name}
                    _save(objectives)
                    return o["key_results"][i]
            raise HTTPException(status_code=404, detail="Key Result not found")
    raise HTTPException(status_code=404, detail="Objective not found")


@router.delete("/{objective_id}/key-results/{kr_id}")
def delete_key_result(objective_id: str, kr_id: str):
    objectives = _load()
    for o in objectives:
        if o["id"] == objective_id:
            key_results = o.get("key_results", [])
            new_key_results = [kr for kr in key_results if kr["id"] != kr_id]
            if len(new_key_results) == len(key_results):
                raise HTTPException(status_code=404, detail="Key Result not found")
            o["key_results"] = new_key_results
            _save(objectives)
            return {"deleted": kr_id}
    raise HTTPException(status_code=404, detail="Objective not found")


# ── Progress calculation ──────────────────────────────────────────────────────

@router.get("/{objective_id}/progress")
def get_objective_progress(objective_id: str):
    objectives = _load()
    for o in objectives:
        if o["id"] == objective_id:
            return {"progress": _calculate_progress(o)}
    raise HTTPException(status_code=404, detail="Objective not found")


# ── Related data endpoints ────────────────────────────────────────────────────

@router.get("/{objective_id}/related")
def get_objective_related_data(objective_id: str):
    objectives = _load()
    objective = next((o for o in objectives if o["id"] == objective_id), None)
    if not objective:
        raise HTTPException(status_code=404, detail="Objective not found")

    tasks_data = data_store.load("tasks.json")
    staff_data = data_store.load("staff.json")

    related_tasks = [t for t in tasks_data.get("tasks", []) if t.get("objective_id") == objective_id]

    staff_ids = set()
    for task in related_tasks:
        for member in task.get("members", []):
            staff_ids.add(member["staff_id"])

    related_staff = [s for s in staff_data.get("staff", []) if s["id"] in staff_ids]

    return {"objective": objective, "related_tasks": related_tasks, "related_staff": related_staff}
