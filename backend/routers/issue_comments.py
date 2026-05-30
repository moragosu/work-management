from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
import data_store
from utils.id_generator import short_uuid
from dependencies import get_current_user

router = APIRouter()


class CommentCreate(BaseModel):
    comment: str
    comment_by: str
    parent_id: Optional[str] = None


class CommentUpdate(BaseModel):
    comment: str


@router.get("/{issue_id}/comments")
def list_comments(issue_id: str):
    with data_store.get_conn() as conn:
        rows = conn.execute(
            "SELECT * FROM issue_comments WHERE issue_id=? ORDER BY created_at",
            (issue_id,)
        ).fetchall()
    comments = [dict(r) for r in rows]
    top = [c for c in comments if not c["parent_id"]]
    for c in top:
        c["replies"] = [r for r in comments if r["parent_id"] == c["id"]]
    return top


@router.post("/{issue_id}/comments", status_code=201)
def create_comment(issue_id: str, body: CommentCreate, user: dict = Depends(get_current_user)):
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    new_c = {
        "id": short_uuid("C"),
        "issue_id": issue_id,
        "parent_id": body.parent_id,
        "comment": body.comment,
        "comment_by": body.comment_by,
        "created_by": user["username"],
        "created_at": now,
        "updated_at": None,
    }
    with data_store.get_conn() as conn:
        conn.execute(
            "INSERT INTO issue_comments (id,issue_id,parent_id,comment,comment_by,created_by,created_at) VALUES (?,?,?,?,?,?,?)",
            (new_c["id"], issue_id, body.parent_id, body.comment, body.comment_by, user["username"], now),
        )
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
        updated_at = datetime.now().strftime("%Y-%m-%d %H:%M")
        conn.execute(
            "UPDATE issue_comments SET comment=?, updated_at=? WHERE id=?",
            (body.comment, updated_at, comment_id),
        )
    return {**dict(row), "comment": body.comment, "updated_at": updated_at}


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
