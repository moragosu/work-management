from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, field_validator
from typing import List, Optional
import data_store

router = APIRouter()


class TeamMember(BaseModel):
    name: str
    role: str
    contribution: int


class KeyResult(BaseModel):
    id: str
    name: str
    progress: int = 0

    @field_validator('progress')
    @classmethod
    def validate_progress(cls, v: int) -> int:
        return max(0, min(100, v))


class Objective(BaseModel):
    id: str
    name: str
    pl: str
    team_members: List[TeamMember] = []
    tech_stack: str = ""
    key_results: List[KeyResult] = []
    status: str = "진행중"


class ObjectiveUpdate(BaseModel):
    name: Optional[str] = None
    pl: Optional[str] = None
    team_members: Optional[List[TeamMember]] = None
    tech_stack: Optional[str] = None
    key_results: Optional[List[KeyResult]] = None
    status: Optional[str] = None


class KeyResultCreate(BaseModel):
    id: str
    name: str
    progress: int = 0


class KeyResultUpdate(BaseModel):
    name: Optional[str] = None
    progress: Optional[int] = None


def _load() -> list:
    data = data_store.load("okrs.json")
    return data.get("objectives", [])


def _save(objectives: list) -> None:
    data_store.save("okrs.json", {"objectives": objectives})


def _calculate_progress(objective: dict) -> int:
    """Calculate objective progress as average of key results."""
    key_results = objective.get("key_results", [])
    if not key_results:
        return 0
    total = sum(kr.get("progress", 0) for kr in key_results)
    return total // len(key_results)


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
            if any(kr["id"] == key_result.id for kr in o.get("key_results", [])):
                raise HTTPException(status_code=400, detail="Key Result id already exists")
            o.setdefault("key_results", []).append(key_result.model_dump())
            _save(objectives)
            return key_result
    raise HTTPException(status_code=404, detail="Objective not found")


@router.put("/{objective_id}/key-results/{kr_id}", response_model=KeyResult)
def update_key_result(objective_id: str, kr_id: str, update: KeyResultUpdate):
    objectives = _load()
    for o in objectives:
        if o["id"] == objective_id:
            for i, kr in enumerate(o.get("key_results", [])):
                if kr["id"] == kr_id:
                    patch = update.model_dump(exclude_none=True)
                    o["key_results"][i] = {**kr, **patch}
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