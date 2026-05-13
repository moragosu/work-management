from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, field_validator
from typing import List, Optional
import data_store

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


def _get_next_objective_id() -> str:
    """Generate next objective ID (O1, O2, ...)."""
    objectives = _load()
    if not objectives:
        return "O1"
    max_num = 0
    for o in objectives:
        try:
            num = int(o["id"].replace("O", ""))
            if num > max_num:
                max_num = num
        except (ValueError, KeyError):
            pass
    return f"O{max_num + 1}"


def _get_next_key_result_id(objective: dict) -> str:
    """Generate next key result ID (KR1, KR2, ...)."""
    key_results = objective.get("key_results", [])
    if not key_results:
        return "KR1"
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
    """Calculate objective progress as average of key results."""
    key_results = objective.get("key_results", [])
    if not key_results:
        return 0
    # Each KR counts as equal progress (100 / count)
    return 100 // len(key_results) if key_results else 0


# ── Objective endpoints ────────────────────────────────────────────────────────

@router.get("", response_model=List[Objective])
def list_objectives():
    return _load()


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
    # Auto-generate ID if not provided or "O"
    if not objective.id or objective.id == "O":
        objective.id = _get_next_objective_id()
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
    new_objectives = [o for o in objectives if o["id"] != objective_id]
    if len(new_objectives) == len(objectives):
        raise HTTPException(status_code=404, detail="Objective not found")
    _save(new_objectives)
    return {"deleted": objective_id}


# ── Key Result endpoints ───────────────────────────────────────────────────────

@router.post("/{objective_id}/key-results", response_model=KeyResult, status_code=201)
def add_key_result(objective_id: str, key_result: KeyResultCreate):
    objectives = _load()
    for o in objectives:
        if o["id"] == objective_id:
            # Auto-generate KR ID
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
            progress = _calculate_progress(o)
            return {"progress": progress}
    raise HTTPException(status_code=404, detail="Objective not found")


# ── Utility endpoints ─────────────────────────────────────────────────────────

@router.get("/next-id")
def get_next_id():
    """Get next available objective ID."""
    return {"next_id": _get_next_objective_id()}