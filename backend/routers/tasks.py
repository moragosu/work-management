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


class SubTask(BaseModel):
    id: str
    name: str
    done: bool = False


class SubTaskUpdate(BaseModel):
    name: Optional[str] = None
    done: Optional[bool] = None


class Task(BaseModel):
    id: str
    name: str
    objective_id: str = ""
    target: str = ""
    members: List[TaskMember] = []
    sub_tasks: List[SubTask] = []


class TaskUpdate(BaseModel):
    name: Optional[str] = None
    objective_id: Optional[str] = None
    target: Optional[str] = None
    members: Optional[List[TaskMember]] = None
    sub_tasks: Optional[List[SubTask]] = None


def _load() -> list:
    data = data_store.load("tasks.json")
    return data.get("tasks", [])


def _save(tasks: list) -> None:
    data_store.save("tasks.json", {"tasks": tasks})


def _cascade_delete_ids(ids_to_remove: set, task_name: str = "") -> None:
    """staff.selected_tasks 및 progress에서 해당 ID들 제거."""
    staff_data = data_store.load("staff.json")
    changed = False
    for staff in staff_data.get("staff", []):
        parts = [x.strip() for x in staff.get("selected_tasks", "").split(",") if x.strip()]
        new_parts = [x for x in parts if x not in ids_to_remove]
        if len(new_parts) != len(parts):
            staff["selected_tasks"] = ",".join(new_parts)
            changed = True
    if changed:
        data_store.save("staff.json", staff_data)

    progress_data = data_store.load("progress.json")
    changed = False
    for item in progress_data.get("progress_items", []):
        if item.get("task_id") in ids_to_remove:
            item["task_id"] = ""
            item["task_name"] = task_name
            changed = True
    if changed:
        data_store.save("progress.json", progress_data)


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


@router.put("/{task_id}/sub-tasks/{sub_task_id}")
def update_sub_task(task_id: str, sub_task_id: str, update: SubTaskUpdate):
    tasks = _load()
    for i, t in enumerate(tasks):
        if t["id"] == task_id:
            sub_tasks = t.get("sub_tasks", [])
            for j, st in enumerate(sub_tasks):
                if st["id"] == sub_task_id:
                    patch = update.model_dump(exclude_none=True)
                    sub_tasks[j] = {**st, **patch}
                    tasks[i]["sub_tasks"] = sub_tasks
                    _save(tasks)
                    return sub_tasks[j]
            raise HTTPException(status_code=404, detail="Sub-task not found")
    raise HTTPException(status_code=404, detail="Task not found")


@router.delete("/{task_id}/sub-tasks/{sub_task_id}")
def delete_sub_task(task_id: str, sub_task_id: str):
    tasks = _load()
    for i, t in enumerate(tasks):
        if t["id"] == task_id:
            sub_tasks = t.get("sub_tasks", [])
            st = next((s for s in sub_tasks if s["id"] == sub_task_id), None)
            if not st:
                raise HTTPException(status_code=404, detail="Sub-task not found")
            tasks[i]["sub_tasks"] = [s for s in sub_tasks if s["id"] != sub_task_id]
            _save(tasks)
            _cascade_delete_ids({sub_task_id}, t["name"])
            return {"deleted": sub_task_id}
    raise HTTPException(status_code=404, detail="Task not found")


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
    sub_task_ids = {st["id"] for st in task.get("sub_tasks", [])}
    all_ids = {task_id} | sub_task_ids

    _cascade_delete_ids(all_ids, task_name)

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
