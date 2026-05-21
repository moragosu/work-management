from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from datetime import date
import data_store
from utils.id_generator import short_uuid

router = APIRouter()

CATEGORIES = {"bug": "버그", "feature": "기능요청", "other": "기타"}


def _load():
    data = data_store.load("feedback.json")
    return data.get("feedbacks", [])


def _save(feedbacks):
    data_store.save("feedback.json", {"feedbacks": feedbacks})


class FeedbackCreate(BaseModel):
    category: str
    title: str
    content: str
    author: str


class FeedbackUpdate(BaseModel):
    category: Optional[str] = None
    title: Optional[str] = None
    content: Optional[str] = None
    author: Optional[str] = None


@router.get("")
def list_feedbacks(category: Optional[str] = None):
    feedbacks = _load()
    if category:
        feedbacks = [f for f in feedbacks if f.get("category") == category]
    return sorted(feedbacks, key=lambda f: f.get("created_at", ""), reverse=True)


@router.post("", status_code=201)
def create_feedback(body: FeedbackCreate):
    if body.category not in CATEGORIES:
        raise HTTPException(status_code=400, detail="유효하지 않은 카테고리입니다")
    feedbacks = _load()
    new_f = {
        "id": short_uuid("F"),
        "category": body.category,
        "title": body.title.strip(),
        "content": body.content.strip(),
        "author": body.author.strip(),
        "created_at": date.today().isoformat(),
        "updated_at": None,
    }
    feedbacks.append(new_f)
    _save(feedbacks)
    return new_f


@router.put("/{feedback_id}")
def update_feedback(feedback_id: str, body: FeedbackUpdate):
    feedbacks = _load()
    for f in feedbacks:
        if f["id"] == feedback_id:
            if body.category is not None:
                if body.category not in CATEGORIES:
                    raise HTTPException(status_code=400, detail="유효하지 않은 카테고리입니다")
                f["category"] = body.category
            if body.title is not None:
                f["title"] = body.title.strip()
            if body.content is not None:
                f["content"] = body.content.strip()
            if body.author is not None:
                f["author"] = body.author.strip()
            f["updated_at"] = date.today().isoformat()
            _save(feedbacks)
            return f
    raise HTTPException(status_code=404, detail="Feedback not found")


@router.delete("/{feedback_id}")
def delete_feedback(feedback_id: str):
    feedbacks = _load()
    feedbacks = [f for f in feedbacks if f["id"] != feedback_id]
    _save(feedbacks)
    return {"deleted": feedback_id}
