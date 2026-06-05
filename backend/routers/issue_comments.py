from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
import json
import data_store
from utils.id_generator import short_uuid
from dependencies import get_current_user

router = APIRouter()


class CommentCreate(BaseModel):
    comment: str
    comment_by: str
    parent_id: Optional[str] = None
    requires_answer: bool = False
    tagged_users: list[str] = []


class CommentUpdate(BaseModel):
    comment: str


def _serialize(row: dict) -> dict:
    row = dict(row)
    if isinstance(row.get("tagged_users"), str):
        try:
            row["tagged_users"] = json.loads(row["tagged_users"])
        except Exception:
            row["tagged_users"] = []
    return row


@router.get("/{issue_id}/comments")
def list_comments(issue_id: str):
    with data_store.get_conn() as conn:
        rows = conn.execute(
            "SELECT * FROM issue_comments WHERE issue_id=? ORDER BY created_at",
            (issue_id,)
        ).fetchall()
    comments = [_serialize(dict(r)) for r in rows]
    top = [c for c in comments if not c["parent_id"]]
    for c in top:
        c["replies"] = [r for r in comments if r["parent_id"] == c["id"]]
    return top


@router.post("/{issue_id}/comments", status_code=201)
def create_comment(issue_id: str, body: CommentCreate, user: dict = Depends(get_current_user)):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    tagged_json = json.dumps(body.tagged_users)
    new_c = {
        "id": short_uuid("C"),
        "issue_id": issue_id,
        "parent_id": body.parent_id,
        "comment": body.comment,
        "comment_by": body.comment_by,
        "created_by": user["username"],
        "requires_answer": int(body.requires_answer),
        "is_answered": 0,
        "tagged_users": body.tagged_users,
        "created_at": now,
        "updated_at": None,
    }
    with data_store.get_conn() as conn:
        conn.execute(
            "INSERT INTO issue_comments (id,issue_id,parent_id,comment,comment_by,created_by,requires_answer,is_answered,tagged_users,created_at) VALUES (?,?,?,?,?,?,?,?,?,?)",
            (new_c["id"], issue_id, body.parent_id, body.comment, body.comment_by, user["username"],
             new_c["requires_answer"], 0, tagged_json, now),
        )
        # 대댓글 등록 시 부모 댓글 자동 answered 처리
        if body.parent_id:
            conn.execute(
                "UPDATE issue_comments SET is_answered=1 WHERE id=? AND requires_answer=1",
                (body.parent_id,)
            )
        issue_row = conn.execute(
            "SELECT task_id, week FROM issues WHERE id=?", (issue_id,)
        ).fetchone()
        existing = conn.execute(
            "SELECT DISTINCT comment_by FROM issue_comments WHERE issue_id=? AND id!=?",
            (issue_id, new_c["id"])
        ).fetchall()
        members = []
        if issue_row and issue_row["task_id"]:
            task_row = conn.execute(
                "SELECT members FROM tasks WHERE id=?", (issue_row["task_id"],)
            ).fetchone()
            members = json.loads(task_row["members"] or "[]") if task_row else []

    if issue_row:
        notified = {user["username"]}
        link = f"/progress?week={issue_row['week']}&focusIssueId={issue_id}"
        if body.requires_answer:
            title = "답변을 요청하는 댓글이 달렸습니다"
        elif body.parent_id:
            title = "이슈 댓글에 답글이 달렸습니다"
        else:
            title = "이슈에 댓글이 달렸습니다"

        # 답변 요구 댓글: tagged_users에게 우선 알림
        if body.requires_answer:
            for name in body.tagged_users:
                resolved = data_store.get_username_for_notification(name)
                if resolved and resolved not in notified:
                    data_store.insert_notification(resolved, "issue_comment", title, body.comment[:50], link)
                    notified.add(resolved)

        for m in members:
            username = m.get("username") or data_store.get_username_for_notification(m.get("name", ""))
            if username and username not in notified:
                data_store.insert_notification(username, "issue_comment", title, body.comment[:50], link)
                notified.add(username)

        for r in existing:
            resolved = data_store.get_username_for_notification(r["comment_by"])
            if resolved and resolved not in notified:
                data_store.insert_notification(resolved, "issue_comment", title, body.comment[:50], link)
                notified.add(resolved)

    new_c["replies"] = []
    return new_c


@router.put("/{issue_id}/comments/{comment_id}")
def update_comment(issue_id: str, comment_id: str, body: CommentUpdate, user: dict = Depends(get_current_user)):
    with data_store.get_conn() as conn:
        row = conn.execute("SELECT * FROM issue_comments WHERE id=?", (comment_id,)).fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Comment not found")
        if not user.get("is_admin") and row["created_by"] != user["username"]:
            raise HTTPException(status_code=403, detail="본인이 작성한 댓글만 수정할 수 있습니다")
        updated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        conn.execute(
            "UPDATE issue_comments SET comment=?, updated_at=? WHERE id=?",
            (body.comment, updated_at, comment_id),
        )
    return {**_serialize(dict(row)), "comment": body.comment, "updated_at": updated_at}


@router.delete("/{issue_id}/comments/{comment_id}")
def delete_comment(issue_id: str, comment_id: str, user: dict = Depends(get_current_user)):
    with data_store.get_conn() as conn:
        row = conn.execute("SELECT created_by, parent_id FROM issue_comments WHERE id=?", (comment_id,)).fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Comment not found")
        if not user.get("is_admin") and row["created_by"] != user["username"]:
            raise HTTPException(status_code=403, detail="본인이 작성한 댓글만 삭제할 수 있습니다")
        # 댓글 삭제 시 대댓글도 함께 삭제
        conn.execute("DELETE FROM issue_comments WHERE id=? OR parent_id=?", (comment_id, comment_id))
    return {"deleted": comment_id}
