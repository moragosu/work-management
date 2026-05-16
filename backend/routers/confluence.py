from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import Optional
import uuid
import data_store

router = APIRouter()


def _load():
    return data_store.load("confluence_links.json").get("links", [])


def _save(links):
    data_store.save("confluence_links.json", {"links": links})


class LinkCreate(BaseModel):
    week: str
    task_id: Optional[str] = None
    url: str


class LinkUpdate(BaseModel):
    url: str


@router.get("")
def get_links(week: Optional[str] = Query(None), task_id: Optional[str] = Query(None)):
    links = _load()
    if week:
        links = [l for l in links if l.get("week") == week]
    if task_id is not None:
        links = [l for l in links if l.get("task_id") == task_id]
    return links


@router.post("", status_code=201)
def create_link(body: LinkCreate):
    links = _load()
    new_link = {
        "id": f"CL{str(uuid.uuid4())[:8].upper()}",
        "week": body.week,
        "task_id": body.task_id,
        "url": body.url,
    }
    links.append(new_link)
    _save(links)
    return new_link


@router.put("/{link_id}")
def update_link(link_id: str, body: LinkUpdate):
    links = _load()
    for l in links:
        if l["id"] == link_id:
            l["url"] = body.url
            _save(links)
            return l
    raise HTTPException(status_code=404, detail="Link not found")


@router.delete("/{link_id}")
def delete_link(link_id: str):
    links = _load()
    links = [l for l in links if l["id"] != link_id]
    _save(links)
    return {"deleted": link_id}
