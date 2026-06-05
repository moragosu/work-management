from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
import json
import data_store
from utils.id_generator import short_uuid
from dependencies import get_current_user

router = APIRouter()        # /api/tasks/{task_id}/comments
router_global = APIRouter()  # /api/task-comments (대시보드용)


class TaskCommentCreate(BaseModel):
    comment: str
    comment_by: str
    week: str
    parent_id: Optional[str] = None
    requires_answer: bool = False
    tagged_users: list[str] = []


class TaskCommentUpdate(BaseModel):
    comment: str
    tagged_users: list[str] = []
    requires_answer: bool = False


def _serialize(row: dict) -> dict:
    row = dict(row)
    if isinstance(row.get("tagged_users"), str):
        try:
            row["tagged_users"] = json.loads(row["tagged_users"])
        except Exception:
            row["tagged_users"] = []
    return row


@router.get("/{task_id}/comments")
def list_task_comments(task_id: str, week: Optional[str] = Query(None)):
    with data_store.get_conn() as conn:
        if week:
            rows = conn.execute(
                "SELECT * FROM task_comments WHERE task_id=? AND week=? ORDER BY created_at",
                (task_id, week)
            ).fetchall()
        else:
            rows = conn.execute(
                "SELECT * FROM task_comments WHERE task_id=? ORDER BY created_at",
                (task_id,)
            ).fetchall()
    comments = [_serialize(dict(r)) for r in rows]
    top = [c for c in comments if not c["parent_id"]]
    for c in top:
        c["replies"] = [r for r in comments if r["parent_id"] == c["id"]]
    return top


@router_global.get("")
def list_all_task_comments(week: Optional[str] = Query(None)):
    """대시보드용 전체 과제 댓글 조회."""
    with data_store.get_conn() as conn:
        if week:
            rows = conn.execute(
                "SELECT * FROM task_comments WHERE week=? ORDER BY created_at",
                (week,)
            ).fetchall()
        else:
            rows = conn.execute(
                "SELECT * FROM task_comments ORDER BY created_at"
            ).fetchall()
    return [_serialize(dict(r)) for r in rows]


@router.post("/{task_id}/comments", status_code=201)
def create_task_comment(task_id: str, body: TaskCommentCreate, user: dict = Depends(get_current_user)):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    tagged_json = json.dumps(body.tagged_users)
    new_c = {
        "id": short_uuid("C"),
        "task_id": task_id,
        "week": body.week,
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
            "INSERT INTO task_comments (id,task_id,week,parent_id,comment,comment_by,created_by,requires_answer,is_answered,tagged_users,created_at) VALUES (?,?,?,?,?,?,?,?,?,?,?)",
            (new_c["id"], task_id, body.week, body.parent_id, body.comment, body.comment_by,
             user["username"], new_c["requires_answer"], 0, tagged_json, now),
        )
        if body.parent_id:
            conn.execute(
                "UPDATE task_comments SET is_answered=1 WHERE id=? AND requires_answer=1",
                (body.parent_id,)
            )

    # 알림 발송
    notified = {user["username"]}
    link = f"/progress?week={body.week}&taskId={task_id}&commentId={new_c['id']}"
    base_link = f"/progress?week={body.week}&taskId={task_id}"
    if body.requires_answer:
        title = "답변을 요청하는 과제 댓글이 달렸습니다"
        for name in body.tagged_users:
            resolved = data_store.get_username_for_notification(name)
            if resolved and resolved not in notified:
                data_store.insert_notification(resolved, "comment_tagged", title, body.comment[:50], link)
                notified.add(resolved)
    elif body.tagged_users:
        title = "과제 댓글에서 태그되었습니다"
        for name in body.tagged_users:
            resolved = data_store.get_username_for_notification(name)
            if resolved and resolved not in notified:
                data_store.insert_notification(resolved, "task_comment", title, body.comment[:50], base_link)
                notified.add(resolved)
    elif body.parent_id:
        title = "과제 댓글에 답글이 달렸습니다"
    else:
        title = "과제에 댓글이 달렸습니다"

    new_c["replies"] = []
    data_store.bump_data_version()
    return new_c


@router.put("/{task_id}/comments/{comment_id}")
def update_task_comment(task_id: str, comment_id: str, body: TaskCommentUpdate, user: dict = Depends(get_current_user)):
    with data_store.get_conn() as conn:
        row = conn.execute("SELECT * FROM task_comments WHERE id=?", (comment_id,)).fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Comment not found")
        if not user.get("is_admin") and row["created_by"] != user["username"]:
            raise HTTPException(status_code=403, detail="본인이 작성한 댓글만 수정할 수 있습니다")
        updated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        tagged_json = json.dumps(body.tagged_users)
        conn.execute(
            "UPDATE task_comments SET comment=?, tagged_users=?, requires_answer=?, updated_at=? WHERE id=?",
            (body.comment, tagged_json, int(body.requires_answer), updated_at, comment_id),
        )
        # requires_answer 해제 시 기존 comment_tagged 알림 자동 삭제
        if row["requires_answer"] and not body.requires_answer:
            conn.execute(
                "DELETE FROM notifications WHERE type='comment_tagged' AND link LIKE ?",
                (f"%commentId={comment_id}%",)
            )

    # 수정 시 알림: 새로 추가된 tagged_users 또는 requires_answer가 켜진 경우
    if body.tagged_users:
        old_requires = bool(row["requires_answer"])
        old_tagged = _serialize(dict(row))["tagged_users"]
        notified = {user["username"]}
        week = row["week"]
        base_link = f"/progress?week={week}&taskId={task_id}"

        if body.requires_answer:
            title = "답변을 요청하는 과제 댓글이 달렸습니다"
            tagged_link = f"{base_link}&commentId={comment_id}"
            to_notify = body.tagged_users if not old_requires else [n for n in body.tagged_users if n not in old_tagged]
            for name in to_notify:
                resolved = data_store.get_username_for_notification(name)
                if resolved and resolved not in notified:
                    data_store.insert_notification(resolved, "comment_tagged", title, body.comment[:50], tagged_link)
                    notified.add(resolved)
        else:
            title = "과제 댓글에서 태그되었습니다"
            new_tagged = [n for n in body.tagged_users if n not in old_tagged]
            for name in new_tagged:
                resolved = data_store.get_username_for_notification(name)
                if resolved and resolved not in notified:
                    data_store.insert_notification(resolved, "task_comment", title, body.comment[:50], base_link)
                    notified.add(resolved)

    data_store.bump_data_version()
    return {
        **_serialize(dict(row)),
        "comment": body.comment,
        "tagged_users": body.tagged_users,
        "requires_answer": int(body.requires_answer),
        "updated_at": updated_at,
    }


@router.delete("/{task_id}/comments/{comment_id}")
def delete_task_comment(task_id: str, comment_id: str, user: dict = Depends(get_current_user)):
    renotify_parent = None
    with data_store.get_conn() as conn:
        row = conn.execute("SELECT * FROM task_comments WHERE id=?", (comment_id,)).fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Comment not found")
        if not user.get("is_admin") and row["created_by"] != user["username"]:
            raise HTTPException(status_code=403, detail="본인이 작성한 댓글만 삭제할 수 있습니다")

        parent_id = row["parent_id"]
        if parent_id:
            # 답글 삭제 시: 남은 형제 답글 수 확인
            sibling_cnt = conn.execute(
                "SELECT COUNT(*) as cnt FROM task_comments WHERE parent_id=? AND id!=?",
                (parent_id, comment_id)
            ).fetchone()["cnt"]
            conn.execute("DELETE FROM task_comments WHERE id=?", (comment_id,))
            if sibling_cnt == 0:
                # 남은 답글 없음 → 부모 is_answered 복원
                parent = conn.execute("SELECT * FROM task_comments WHERE id=?", (parent_id,)).fetchone()
                if parent and parent["requires_answer"]:
                    conn.execute("UPDATE task_comments SET is_answered=0 WHERE id=?", (parent_id,))
                    renotify_parent = dict(parent)
        else:
            conn.execute("DELETE FROM task_comments WHERE id=? OR parent_id=?", (comment_id, comment_id))
            if row["requires_answer"]:
                conn.execute(
                    "DELETE FROM notifications WHERE type='comment_tagged' AND link LIKE ?",
                    (f"%commentId={comment_id}%",)
                )

    # 부모 댓글 미답변 복원 시 재알림 발송 (태그된 모든 사람에게 재발송)
    if renotify_parent:
        tagged = json.loads(renotify_parent.get("tagged_users") or "[]")
        link = f"/progress?week={renotify_parent['week']}&taskId={task_id}&commentId={parent_id}"
        title = "답변을 요청하는 과제 댓글이 달렸습니다"
        seen = set()
        for name in tagged:
            resolved = data_store.get_username_for_notification(name)
            if resolved and resolved not in seen:
                data_store.insert_notification(resolved, "comment_tagged", title, renotify_parent["comment"][:50], link)
                seen.add(resolved)

    data_store.bump_data_version()
    return {"deleted": comment_id, "parent_unanswered": parent_id if renotify_parent else None}
