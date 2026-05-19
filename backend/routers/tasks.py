from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import data_store
from utils.id_generator import next_counter_id, get_reusable_ids, get_next_id_preview, sync_counter

router = APIRouter()


class TaskMember(BaseModel):
    staff_id: str
    name: str
    role: str = ""


class Task(BaseModel):
    id: str
    name: str
    objective_id: str = ""
    target: str = ""
    members: List[TaskMember] = []


class TaskUpdate(BaseModel):
    name: Optional[str] = None
    objective_id: Optional[str] = None
    target: Optional[str] = None
    members: Optional[List[TaskMember]] = None


def _load() -> list:
    data = data_store.load("tasks.json")
    return data.get("tasks", [])


def _save(tasks: list) -> None:
    data_store.save("tasks.json", {"tasks": tasks})


# ── Task endpoints ─────────────────────────────────────────────────────────────

@router.get("", response_model=List[Task])
def list_tasks(objective_id: Optional[str] = None):
    tasks = _load()
    if objective_id:
        tasks = [t for t in tasks if t.get("objective_id") == objective_id]
    return tasks


@router.get("/next-id")
def get_next_id():
    tasks = _load()
    return {"next_id": get_next_id_preview("T", tasks)}


@router.get("/reusable-ids")
def get_reusable_task_ids():
    tasks = _load()
    return {"reusable_ids": get_reusable_ids(tasks, "T")}


@router.get("/{task_id}", response_model=Task)
def get_task(task_id: str):
    tasks = _load()
    for t in tasks:
        if t["id"] == task_id:
            return t
    raise HTTPException(status_code=404, detail="Task not found")


@router.post("", response_model=Task, status_code=201)
def create_task(task: Task):
    tasks = _load()
    if not task.id:
        task.id = next_counter_id("T", tasks)
    else:
        sync_counter("T", task.id, tasks)
    if any(t["id"] == task.id for t in tasks):
        raise HTTPException(status_code=400, detail="Task id already exists")
    tasks.append(task.model_dump())
    _save(tasks)
    return task


class BulkTargetUpdate(BaseModel):
    task_ids: List[str]
    target: str


@router.put("/bulk-target")
def bulk_update_target(update: BulkTargetUpdate):
    tasks = _load()
    id_set = set(update.task_ids)
    count = 0
    for i, t in enumerate(tasks):
        if t["id"] in id_set:
            tasks[i] = {**t, "target": update.target}
            count += 1
    _save(tasks)
    return {"updated": count}


@router.put("/{task_id}", response_model=Task)
def update_task(task_id: str, update: TaskUpdate):
    tasks = _load()
    for i, t in enumerate(tasks):
        if t["id"] == task_id:
            old_objective_id = t.get("objective_id", "")
            new_objective_id = update.objective_id if update.objective_id is not None else old_objective_id
            patch = update.model_dump(exclude_none=True)
            tasks[i] = {**t, **patch}
            _save(tasks)
            if old_objective_id != new_objective_id:
                member_ids = {m["staff_id"] for m in t.get("members", [])}
                if member_ids:
                    _sync_staff_okrs(member_ids, old_objective_id, new_objective_id, tasks)
            return tasks[i]
    raise HTTPException(status_code=404, detail="Task not found")


def _sync_staff_okrs(member_ids: set, old_obj_id: str, new_obj_id: str, all_tasks: list):
    """task objective_id 변경 시 관련 staff.okrs 자동 동기화."""
    staff_data = data_store.load("staff.json")
    changed = False
    for staff in staff_data.get("staff", []):
        if staff["id"] not in member_ids:
            continue
        okrs = [x.strip() for x in staff.get("okrs", "").split(",") if x.strip()]
        if old_obj_id:
            still_connected = any(
                t.get("objective_id") == old_obj_id and
                any(m["staff_id"] == staff["id"] for m in t.get("members", []))
                for t in all_tasks
            )
            if not still_connected and old_obj_id in okrs:
                okrs.remove(old_obj_id)
        if new_obj_id and new_obj_id not in okrs:
            okrs.append(new_obj_id)
        staff["okrs"] = ",".join(okrs)
        changed = True
    if changed:
        data_store.save("staff.json", staff_data)


@router.delete("/{task_id}")
def delete_task(task_id: str):
    tasks = _load()
    task = next((t for t in tasks if t["id"] == task_id), None)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    task_name = task["name"]

    # Cascade: staff.selected_tasks에서 제거
    staff_data = data_store.load("staff.json")
    staff_changed = False
    for staff in staff_data.get("staff", []):
        tasks_str = staff.get("selected_tasks", "")
        if tasks_str:
            ids = [x.strip() for x in tasks_str.split(",") if x.strip()]
            new_ids = [x for x in ids if x != task_id]
            if len(new_ids) != len(ids):
                staff["selected_tasks"] = ",".join(new_ids)
                staff_changed = True
    if staff_changed:
        data_store.save("staff.json", staff_data)

    # Cascade: progress의 task_id를 초기화하고 task_name에 이름 텍스트 보존 (이력 보존)
    progress_data = data_store.load("progress.json")
    progress_changed = False
    for item in progress_data.get("progress_items", []):
        if item.get("task_id") == task_id:
            item["task_id"] = ""
            item["task_name"] = task_name
            progress_changed = True
    if progress_changed:
        data_store.save("progress.json", progress_data)

    new_tasks = [t for t in tasks if t["id"] != task_id]
    _save(new_tasks)
    return {"deleted": task_id}


# ── Related data endpoints ────────────────────────────────────────────────────

@router.get("/{task_id}/related")
def get_task_related_data(task_id: str):
    tasks = _load()
    task = next((t for t in tasks if t["id"] == task_id), None)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    objectives_data = data_store.load("okrs.json")
    staff_data = data_store.load("staff.json")

    related_objective = None
    if task.get("objective_id"):
        related_objective = next(
            (o for o in objectives_data.get("objectives", []) if o["id"] == task["objective_id"]), None
        )

    related_staff = [
        s for s in staff_data.get("staff", [])
        if any(m["staff_id"] == s["id"] for m in task.get("members", []))
    ]

    return {"task": task, "related_objective": related_objective, "related_staff": related_staff}
