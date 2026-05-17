from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import data_store
from utils.id_generator import next_sequential_id

router = APIRouter()


class TaskMember(BaseModel):
    staff_id: str
    name: str
    role: str = ""


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
    return next_sequential_id(_load(), "T")


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


# ── Related data endpoints ────────────────────────────────────────────────────

@router.get("/{task_id}/related")
def get_task_related_data(task_id: str):
    """Get related objective and staff data for a task"""
    tasks = _load()
    task = next((t for t in tasks if t["id"] == task_id), None)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    # Load related data
    import data_store
    objectives_data = data_store.load("okrs.json")
    staff_data = data_store.load("staff.json")
    
    result = {
        "task": task,
        "related_objective": None,
        "related_staff": []
    }
    
    # Get related objective
    if task.get("objective_id"):
        objective = next((o for o in objectives_data.get("objectives", []) if o["id"] == task["objective_id"]), None)
        if objective:
            result["related_objective"] = objective
    
    # Get related staff
    for member in task.get("members", []):
        staff = next((s for s in staff_data.get("staff", []) if s["id"] == member["staff_id"]), None)
        if staff:
            result["related_staff"].append(staff)
    
    return result
