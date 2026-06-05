from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
import json
import data_store
from utils.id_generator import short_uuid
from dependencies import get_current_user

router = APIRouter()
router_global = APIRouter()  # /api/issue-comments (대시보드용)


class CommentCreate(BaseModel):
    comment: str
    comment_by: str
    parent_id: Optional[str] = None
    requires_answer: bool = False
    tagged_users: list[str] = []


class CommentUpdate(BaseModel):
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


@router_global.get("")
def list_all_issue_comments(week: Optional[str] = Query(None)):
    """대시보드용 전체 이슈 댓글 조회 (issues 테이블에서 week, task_id 조인)."""
    with data_store.get_conn() as conn:
        if week:
            rows = conn.execute(
                """SELECT ic.id, ic.issue_id, ic.parent_id, ic.comment, ic.comment_by,
                          ic.created_by, ic.requires_answer, ic.is_answered, ic.tagged_users,
                          ic.created_at, ic.updated_at, iss.week, iss.task_id
                   FROM issue_comments ic
                   LEFT JOIN issues iss ON ic.issue_id = iss.id
                   WHERE iss.week=? AND ic.parent_id IS NULL
                   ORDER BY ic.created_at""",
                (week,)
            ).fetchall()
        else:
            rows = conn.execute(
                """SELECT ic.id, ic.issue_id, ic.parent_id, ic.comment, ic.comment_by,
                          ic.created_by, ic.requires_answer, ic.is_answered, ic.tagged_users,
                          ic.created_at, ic.updated_at, iss.week, iss.task_id
                   FROM issue_comments ic
                   LEFT JOIN issues iss ON ic.issue_id = iss.id
                   WHERE ic.parent_id IS NULL
                   ORDER BY ic.created_at"""
            ).fetchall()
    result = []
    for r in rows:
        d = _serialize(dict(r))
        d["type"] = "issue"
        result.append(d)
    return result


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
        base_link = f"/progress?week={issue_row['week']}&focusIssueId={issue_id}"
        if body.requires_answer:
            title = "답변을 요청하는 댓글이 달렸습니다"
            tagged_link = f"{base_link}&commentId={new_c['id']}"
        elif body.parent_id:
            title = "이슈 댓글에 답글이 달렸습니다"
        else:
            title = "이슈에 댓글이 달렸습니다"

        # tagged_users 알림: requires_answer면 comment_tagged(보호), 아니면 issue_comment
        if body.requires_answer:
            for name in body.tagged_users:
                resolved = data_store.get_username_for_notification(name)
                if resolved and resolved not in notified:
                    data_store.insert_notification(resolved, "comment_tagged", title, body.comment[:50], tagged_link)
                    notified.add(resolved)
        elif body.tagged_users:
            for name in body.tagged_users:
                resolved = data_store.get_username_for_notification(name)
                if resolved and resolved not in notified:
                    data_store.insert_notification(resolved, "issue_comment", title, body.comment[:50], base_link)
                    notified.add(resolved)

        for m in members:
            username = m.get("username") or data_store.get_username_for_notification(m.get("name", ""))
            if username and username not in notified:
                data_store.insert_notification(username, "issue_comment", title, body.comment[:50], base_link)
                notified.add(username)

        for r in existing:
            resolved = data_store.get_username_for_notification(r["comment_by"])
            if resolved and resolved not in notified:
                data_store.insert_notification(resolved, "issue_comment", title, body.comment[:50], base_link)
                notified.add(resolved)

    new_c["replies"] = []
    data_store.bump_data_version()
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
        tagged_json = json.dumps(body.tagged_users)
        conn.execute(
            "UPDATE issue_comments SET comment=?, tagged_users=?, requires_answer=?, updated_at=? WHERE id=?",
            (body.comment, tagged_json, int(body.requires_answer), updated_at, comment_id),
        )
        issue_row = conn.execute("SELECT week FROM issues WHERE id=?", (issue_id,)).fetchone()
        # requires_answer 해제 시 기존 comment_tagged 알림 자동 삭제
        if row["requires_answer"] and not body.requires_answer:
            conn.execute(
                "DELETE FROM notifications WHERE type='comment_tagged' AND link LIKE ?",
                (f"%commentId={comment_id}%",)
            )

    # 수정 시 알림: 새로 추가된 tagged_users 또는 requires_answer가 켜진 경우
    if body.tagged_users and issue_row:
        old_requires = bool(row["requires_answer"])
        old_tagged = _serialize(dict(row))["tagged_users"]
        notified = {user["username"]}
        week = issue_row["week"]
        base_link = f"/progress?week={week}&focusIssueId={issue_id}"

        if body.requires_answer:
            title = "답변을 요청하는 댓글이 달렸습니다"
            tagged_link = f"{base_link}&commentId={comment_id}"
            # requires_answer 새로 켜짐 → 전체 태그 알림 / 이미 켜져 있었으면 신규 추가분만
            to_notify = body.tagged_users if not old_requires else [n for n in body.tagged_users if n not in old_tagged]
            for name in to_notify:
                resolved = data_store.get_username_for_notification(name)
                if resolved and resolved not in notified:
                    data_store.insert_notification(resolved, "comment_tagged", title, body.comment[:50], tagged_link)
                    notified.add(resolved)
        else:
            title = "이슈 댓글에서 태그되었습니다"
            new_tagged = [n for n in body.tagged_users if n not in old_tagged]
            for name in new_tagged:
                resolved = data_store.get_username_for_notification(name)
                if resolved and resolved not in notified:
                    data_store.insert_notification(resolved, "issue_comment", title, body.comment[:50], base_link)
                    notified.add(resolved)

    data_store.bump_data_version()
    return {
        **_serialize(dict(row)),
        "comment": body.comment,
        "tagged_users": body.tagged_users,
        "requires_answer": int(body.requires_answer),
        "updated_at": updated_at,
    }


@router.delete("/{issue_id}/comments/{comment_id}")
def delete_comment(issue_id: str, comment_id: str, user: dict = Depends(get_current_user)):
    renotify_parent = None
    parent_issue_week = None
    with data_store.get_conn() as conn:
        row = conn.execute("SELECT * FROM issue_comments WHERE id=?", (comment_id,)).fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Comment not found")
        if not user.get("is_admin") and row["created_by"] != user["username"]:
            raise HTTPException(status_code=403, detail="본인이 작성한 댓글만 삭제할 수 있습니다")

        parent_id = row["parent_id"]
        if parent_id:
            sibling_cnt = conn.execute(
                "SELECT COUNT(*) as cnt FROM issue_comments WHERE parent_id=? AND id!=?",
                (parent_id, comment_id)
            ).fetchone()["cnt"]
            conn.execute("DELETE FROM issue_comments WHERE id=?", (comment_id,))
            if sibling_cnt == 0:
                parent = conn.execute("SELECT * FROM issue_comments WHERE id=?", (parent_id,)).fetchone()
                if parent and parent["requires_answer"]:
                    conn.execute("UPDATE issue_comments SET is_answered=0 WHERE id=?", (parent_id,))
                    renotify_parent = dict(parent)
                    issue_row = conn.execute("SELECT week FROM issues WHERE id=?", (issue_id,)).fetchone()
                    parent_issue_week = issue_row["week"] if issue_row else None
        else:
            conn.execute("DELETE FROM issue_comments WHERE id=? OR parent_id=?", (comment_id, comment_id))
            if row["requires_answer"]:
                conn.execute(
                    "DELETE FROM notifications WHERE type='comment_tagged' AND link LIKE ?",
                    (f"%commentId={comment_id}%",)
                )

    if renotify_parent and parent_issue_week:
        tagged = json.loads(renotify_parent.get("tagged_users") or "[]")
        link = f"/progress?week={parent_issue_week}&focusIssueId={issue_id}&commentId={parent_id}"
        title = "답변을 요청하는 댓글이 달렸습니다"
        seen = set()
        for name in tagged:
            resolved = data_store.get_username_for_notification(name)
            if resolved and resolved not in seen:
                data_store.insert_notification(resolved, "comment_tagged", title, renotify_parent["comment"][:50], link)
                seen.add(resolved)

    data_store.bump_data_version()
    return {"deleted": comment_id, "parent_unanswered": parent_id if renotify_parent else None}
