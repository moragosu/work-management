from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import List, Optional
from datetime import date
import data_store
from utils.id_generator import short_uuid

router = APIRouter()


class ProgressItem(BaseModel):
    id: Optional[str] = None
    week: str
    objective: str
    task_id: str = ""
    task_name: str = ""
    subtask: str = ""
    planned: str = ""
    result: str = ""
    progress_percent: int = 0
    issue: str = ""
    assignee: str = ""
    solution: str = ""
    images: List[str] = []
    created_at: Optional[str] = None
    updated_at: Optional[str] = None


class ProgressUpdate(BaseModel):
    week: Optional[str] = None
    objective: Optional[str] = None
    task_id: Optional[str] = None
    task_name: Optional[str] = None
    subtask: Optional[str] = None
    planned: Optional[str] = None
    result: Optional[str] = None
    progress_percent: Optional[int] = None
    issue: Optional[str] = None
    assignee: Optional[str] = None
    solution: Optional[str] = None
    images: Optional[List[str]] = None


def _load():
    data = data_store.load("progress.json")
    return data.get("progress_items", [])


def _save(items: list):
    data_store.save("progress.json", {"progress_items": items})


@router.get("", response_model=List[ProgressItem])
def list_progress(
    week: Optional[str] = Query(None),
    objective: Optional[str] = Query(None),
    task_id: Optional[str] = Query(None),
    assignee: Optional[str] = Query(None),
):
    items = _load()
    if week:
        items = [i for i in items if i.get("week") == week]
    if objective:
        items = [i for i in items if i.get("objective") == objective]
    if task_id:
        items = [i for i in items if i.get("task_id") == task_id]
    if assignee:
        items = [i for i in items if i.get("assignee") == assignee]
    return items


@router.get("/weeks")
def list_weeks():
    items = _load()
    weeks = sorted(set(i.get("week", "") for i in items if i.get("week")),
                   key=lambda w: int(w[1:]) if w[1:].isdigit() else 0)
    return {"weeks": weeks}


@router.get("/{item_id}", response_model=ProgressItem)
def get_item(item_id: str):
    items = _load()
    for i in items:
        if i["id"] == item_id:
            return i
    raise HTTPException(status_code=404, detail="Progress item not found")


@router.post("", response_model=ProgressItem, status_code=201)
def create_item(item: ProgressItem):
    items = _load()
    today = date.today().isoformat()
    new_item = item.model_dump()
    new_item["id"] = short_uuid("P")
    new_item["created_at"] = today
    new_item["updated_at"] = today
    items.append(new_item)
    _save(items)
    return new_item


@router.put("/{item_id}", response_model=ProgressItem)
def update_item(item_id: str, update: ProgressUpdate):
    items = _load()
    for i, item in enumerate(items):
        if item["id"] == item_id:
            patch = update.model_dump(exclude_none=True)
            items[i] = {**item, **patch, "updated_at": date.today().isoformat()}
            _save(items)
            return items[i]
    raise HTTPException(status_code=404, detail="Progress item not found")


@router.delete("/{item_id}")
def delete_item(item_id: str):
    items = _load()
    new_items = [i for i in items if i["id"] != item_id]
    if len(new_items) == len(items):
        raise HTTPException(status_code=404, detail="Progress item not found")
    _save(new_items)
    return {"deleted": item_id}