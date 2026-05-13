from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import data_store

router = APIRouter()


class TaskMember(BaseModel):
    staff_id: str
    name: str


class Task(BaseModel):
    id: str
    name: str
    objective_id: str = ""
    members: List[TaskMember] = []


class TaskUpdate(BaseModel):
    name: Optional[str] = None
    objective_id: Optional[str] = None
    members: Optional[List[TaskMember]] = None


def _load() -> list:
    data = data_store.load("tasks.json")
    return data.get("tasks", [])


def _save(tasks: list) -> None:
    data_store.save("tasks.json", {"tasks": tasks})


def _get_next_task_id() -> str:
    """Generate next task ID (T1, T2, ...)."""
    tasks = _load()
    if not tasks:
        return "T1"
    max_num = 0
    for t in tasks:
        try:
            num = int(t["id"].replace("T", ""))
            if num > max_num:
                max_num = num
        except (ValueError, KeyError):
            pass
    return f"T{max_num + 1}"


# ── Task endpoints ─────────────────────────────────────────────────────────────

@router.get("", response_model=List[Task])
def list_tasks(objective_id: Optional[str] = None):
    tasks = _load()
    if objective_id:
        tasks = [t for t in tasks if t.get("objective_id") == objective_id]
    return tasks


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
    # Auto-generate ID if not provided
    if not task.id:
        task.id = _get_next_task_id()
    if any(t["id"] == task.id for t in tasks):
        raise HTTPException(status_code=400, detail="Task id already exists")
    tasks.append(task.model_dump())
    _save(tasks)
    return task


@router.put("/{task_id}", response_model=Task)
def update_task(task_id: str, update: TaskUpdate):
    tasks = _load()
    for i, t in enumerate(tasks):
        if t["id"] == task_id:
            patch = update.model_dump(exclude_none=True)
            tasks[i] = {**t, **patch}
            _save(tasks)
            return tasks[i]
    raise HTTPException(status_code=404, detail="Task not found")


@router.delete("/{task_id}")
def delete_task(task_id: str):
    tasks = _load()
    new_tasks = [t for t in tasks if t["id"] != task_id]
    if len(new_tasks) == len(tasks):
        raise HTTPException(status_code=404, detail="Task not found")
    _save(new_tasks)
    return {"deleted": task_id}


# ── Utility endpoints ─────────────────────────────────────────────────────────

@router.get("/next-id")
def get_next_id():
    """Get next available task ID."""
    return {"next_id": _get_next_task_id()}