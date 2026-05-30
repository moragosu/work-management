from fastapi import APIRouter, HTTPException, Query, Depends
from pydantic import BaseModel
from typing import Optional
from datetime import date
import data_store
from utils.id_generator import short_uuid
from dependencies import get_current_user

router = APIRouter()


class IssueCreate(BaseModel):
    task_id: str
    week: str
    issue: str
    assignee: str


class IssueUpdate(BaseModel):
    issue: Optional[str] = None
    assignee: Optional[str] = None


def _load():
    return data_store.load("issues.json").get("issues", [])


def _save(issues: list):
    data_store.save("issues.json", {"issues": issues})


@router.get("")
def list_issues(
    week: Optional[str] = Query(None),
    task_id: Optional[str] = Query(None),
):
    items = _load()
    if week:
        items = [i for i in items if i.get("week") == week]
    if task_id:
        items = [i for i in items if i.get("task_id") == task_id]
    return items


@router.post("", status_code=201)
def create_issue(body: IssueCreate, user: dict = Depends(get_current_user)):
    items = _load()
    today = date.today().isoformat()
    new_item = {
        "id": short_uuid("I"),
        "task_id": body.task_id,
        "week": body.week,
        "issue": body.issue,
        "assignee": body.assignee,
        "created_by": user["username"],
        "created_at": today,
        "updated_at": today,
    }
    items.append(new_item)
    _save(items)
    # 알림: 담당자에게
    recipient = data_store.get_username_for_notification(body.assignee)
    data_store.insert_notification(
        recipient, "issue_assigned",
        "담당 과제에 이슈가 등록되었습니다",
        body.issue[:50],
        f"/progress?week={body.week}&focusIssueId={new_item['id']}",
    )
    return new_item


@router.put("/{issue_id}")
def update_issue(issue_id: str, body: IssueUpdate):
    items = _load()
    for i, item in enumerate(items):
        if item["id"] == issue_id:
            patch = body.model_dump(exclude_none=True)
            items[i] = {**item, **patch, "updated_at": date.today().isoformat()}
            _save(items)
            return items[i]
    raise HTTPException(status_code=404, detail="Issue not found")


@router.delete("/{issue_id}")
def delete_issue(issue_id: str, user: dict = Depends(get_current_user)):
    items = _load()
    target = next((i for i in items if i["id"] == issue_id), None)
    if not target:
        raise HTTPException(status_code=404, detail="Issue not found")
    if user["role"] != "admin" and target.get("created_by") != user["username"]:
        raise HTTPException(status_code=403, detail="본인이 작성한 이슈만 삭제할 수 있습니다")
    _save([i for i in items if i["id"] != issue_id])
    return {"deleted": issue_id}
