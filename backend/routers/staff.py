from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import List, Optional
import uuid
import data_store

router = APIRouter()


class StaffMember(BaseModel):
    id: Optional[str] = None
    name: str
    role: str = ""
    main_skills: str = ""
    sub_skills: str = ""
    learning: str = ""
    desired_field: str = ""
    okrs: str = ""  # 연결된 Objective IDs (콤마 구분)
    selected_tasks: str = ""  # 선택된 과제 IDs (콤마 구분) - 새로 추가
    task_ids: List[str] = []  # 연결된 과제 IDs


class StaffUpdate(BaseModel):
    name: Optional[str] = None
    role: Optional[str] = None
    main_skills: Optional[str] = None
    sub_skills: Optional[str] = None
    learning: Optional[str] = None
    desired_field: Optional[str] = None
    okrs: Optional[str] = None
    selected_tasks: Optional[str] = None  # 새로 추가
    task_ids: Optional[List[str]] = None


def _load():
    data = data_store.load("staff.json")
    return data.get("staff", [])


def _save(staff: list):
    data_store.save("staff.json", {"staff": staff})


@router.get("", response_model=List[StaffMember])
def list_staff(search: Optional[str] = Query(None)):
    staff = _load()
    if search:
        q = search.lower()
        staff = [
            s for s in staff
            if q in s.get("name", "").lower()
            or q in s.get("main_skills", "").lower()
            or q in s.get("sub_skills", "").lower()
            or q in s.get("learning", "").lower()
            or q in s.get("okrs", "").lower()
        ]
    return staff


@router.get("/{staff_id}", response_model=StaffMember)
def get_staff(staff_id: str):
    staff = _load()
    for s in staff:
        if s["id"] == staff_id:
            return s
    raise HTTPException(status_code=404, detail="Staff member not found")


@router.post("", response_model=StaffMember, status_code=201)
def create_staff(member: StaffMember):
    staff = _load()
    new_member = member.model_dump()
    new_member["id"] = f"S{str(uuid.uuid4())[:8].upper()}"
    staff.append(new_member)
    _save(staff)
    return new_member


@router.put("/{staff_id}", response_model=StaffMember)
def update_staff(staff_id: str, update: StaffUpdate):
    staff = _load()
    for i, s in enumerate(staff):
        if s["id"] == staff_id:
            patch = update.model_dump(exclude_none=True)
            staff[i] = {**s, **patch}
            _save(staff)
            return staff[i]
    raise HTTPException(status_code=404, detail="Staff member not found")


@router.delete("/{staff_id}")
def delete_staff(staff_id: str):
    staff = _load()
    new_staff = [s for s in staff if s["id"] != staff_id]
    if len(new_staff) == len(staff):
        raise HTTPException(status_code=404, detail="Staff member not found")
    _save(new_staff)
    return {"deleted": staff_id}


# ── Related data endpoints ────────────────────────────────────────────────────

@router.get("/{staff_id}/related")
def get_staff_related_data(staff_id: str):
    """Get related objectives and tasks data for a staff member"""
    staff = _load()
    member = next((s for s in staff if s["id"] == staff_id), None)
    if not member:
        raise HTTPException(status_code=404, detail="Staff member not found")
    
    # Load related data
    import data_store
    tasks_data = data_store.load("tasks.json")
    objectives_data = data_store.load("okrs.json")
    
    result = {
        "staff": member,
        "related_tasks": [],
        "related_objectives": []
    }
    
    # Get related tasks (where this staff is a member)
    related_tasks = []
    for task in tasks_data.get("tasks", []):
        if any(member.get("staff_id") == staff_id for member in task.get("members", [])):
            related_tasks.append(task)
    result["related_tasks"] = related_tasks
    
    # Get related objectives (from tasks and direct okrs field)
    objective_ids = set()
    
    # From tasks
    for task in related_tasks:
        if task.get("objective_id"):
            objective_ids.add(task["objective_id"])
    
    # From direct okrs field
    if member.get("okrs"):
        for obj_id in member["okrs"].split(","):
            obj_id = obj_id.strip()
            if obj_id:
                objective_ids.add(obj_id)
    
    for obj_id in objective_ids:
        objective = next((o for o in objectives_data.get("objectives", []) if o["id"] == obj_id), None)
        if objective:
            result["related_objectives"].append(objective)
    
    return result
