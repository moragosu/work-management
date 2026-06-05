from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from dependencies import get_current_user
import data_store
import auth_utils
import re
import asyncio
from datetime import datetime

router = APIRouter()


def _is_comment_unanswered(conn, link: str) -> bool:
    """comment_tagged 알림 링크에서 commentId 추출 후 미답변 여부 반환.
    requires_answer가 해제됐거나 댓글이 삭제된 경우 False."""
    m = re.search(r'commentId=([^&]+)', link or "")
    if not m:
        return False
    cid = m.group(1)
    row_tc = conn.execute("SELECT requires_answer, is_answered FROM task_comments WHERE id=?", (cid,)).fetchone()
    row_ic = conn.execute("SELECT requires_answer, is_answered FROM issue_comments WHERE id=?", (cid,)).fetchone()
    if row_tc:
        return bool(row_tc["requires_answer"]) and not bool(row_tc["is_answered"])
    if row_ic:
        return bool(row_ic["requires_answer"]) and not bool(row_ic["is_answered"])
    return False


@router.get("")
def list_notifications(user: dict = Depends(get_current_user)):
    with data_store.get_conn() as conn:
        rows = conn.execute(
            "SELECT * FROM notifications WHERE recipient=? ORDER BY created_at DESC",
            (user["username"],)
        ).fetchall()
        notifications = [dict(r) for r in rows]
        # question_tagged / comment_tagged: 미답변 여부를 실시간 반영
        qid_map = {}
        cid_pending = set()
        for n in notifications:
            if n["type"] == "question_tagged":
                m = re.search(r'focusQuestion=([^&]+)', n["link"] or "")
                if m:
                    qid_map[n["id"]] = m.group(1)
            elif n["type"] == "comment_tagged":
                if _is_comment_unanswered(conn, n["link"]):
                    cid_pending.add(n["id"])
        answered_q = set()
        for nid, qid in qid_map.items():
            if conn.execute("SELECT 1 FROM answers WHERE question_id=?", (qid,)).fetchone():
                answered_q.add(nid)
        for n in notifications:
            n["is_pending"] = (
                (n["id"] in qid_map and n["id"] not in answered_q)
                or n["id"] in cid_pending
            )
    return notifications


@router.get("/unread-count")
def unread_count(user: dict = Depends(get_current_user)):
    with data_store.get_conn() as conn:
        row = conn.execute(
            "SELECT COUNT(*) as cnt FROM notifications WHERE recipient=? AND is_read=0",
            (user["username"],)
        ).fetchone()
    return {"count": row["cnt"]}


@router.delete("")
def delete_all_notifications(user: dict = Depends(get_current_user)):
    """전체 삭제 — 미답변 question_tagged / comment_tagged는 제외."""
    with data_store.get_conn() as conn:
        rows = conn.execute(
            "SELECT id, type, link FROM notifications WHERE recipient=?",
            (user["username"],)
        ).fetchall()
        deletable = []
        for n in rows:
            if n["type"] == "question_tagged":
                m = re.search(r'focusQuestion=([^&]+)', n["link"] or "")
                if m:
                    has_answer = conn.execute(
                        "SELECT 1 FROM answers WHERE question_id=?", (m.group(1),)
                    ).fetchone()
                    if has_answer:
                        deletable.append(n["id"])
                else:
                    deletable.append(n["id"])
            elif n["type"] == "comment_tagged":
                if not _is_comment_unanswered(conn, n["link"]):
                    deletable.append(n["id"])
            else:
                deletable.append(n["id"])
        if deletable:
            ph = ",".join("?" * len(deletable))
            conn.execute(f"DELETE FROM notifications WHERE id IN ({ph})", deletable)
    return {"deleted": len(deletable) if deletable else 0}


@router.patch("/{nid}/read")
def mark_read(nid: str, user: dict = Depends(get_current_user)):
    with data_store.get_conn() as conn:
        conn.execute(
            "UPDATE notifications SET is_read=1 WHERE id=? AND recipient=?",
            (nid, user["username"])
        )
    return {"ok": True}


@router.patch("/read-all")
def mark_all_read(user: dict = Depends(get_current_user)):
    with data_store.get_conn() as conn:
        conn.execute(
            "UPDATE notifications SET is_read=1 WHERE recipient=?",
            (user["username"],)
        )
    return {"ok": True}


@router.delete("/{nid}")
def delete_notification(nid: str, user: dict = Depends(get_current_user)):
    with data_store.get_conn() as conn:
        notif = conn.execute(
            "SELECT * FROM notifications WHERE id=? AND recipient=?",
            (nid, user["username"])
        ).fetchone()
        if not notif:
            raise HTTPException(status_code=404, detail="알림을 찾을 수 없습니다")
        # question_tagged / comment_tagged: 미답변 상태면 삭제 불가
        if notif["type"] == "question_tagged":
            m = re.search(r'focusQuestion=([^&]+)', notif["link"] or "")
            if m:
                qid = m.group(1)
                has_answer = conn.execute(
                    "SELECT 1 FROM answers WHERE question_id=?", (qid,)
                ).fetchone()
                if not has_answer:
                    raise HTTPException(
                        status_code=400,
                        detail="해당 질문에 답변하기 전까지 삭제할 수 없습니다"
                    )
        elif notif["type"] == "comment_tagged":
            if _is_comment_unanswered(conn, notif["link"]):
                raise HTTPException(
                    status_code=400,
                    detail="해당 댓글에 답변하기 전까지 삭제할 수 없습니다"
                )
        conn.execute("DELETE FROM notifications WHERE id=?", (nid,))
    return {"ok": True}


@router.get("/stream")
async def notification_stream(token: str = Query(...)):
    """SSE 스트림 — EventSource는 커스텀 헤더를 보낼 수 없어 토큰을 쿼리 파라미터로 수신."""
    payload = auth_utils.decode_token(token)
    if not payload or "sub" not in payload:
        raise HTTPException(status_code=401, detail="인증이 필요합니다")
    with data_store.get_conn() as conn:
        row = conn.execute("SELECT username FROM users WHERE username=?", (payload["sub"],)).fetchone()
    if not row:
        raise HTTPException(status_code=401, detail="사용자를 찾을 수 없습니다")
    username = row["username"]

    def _check_new(since: str):
        with data_store.get_conn() as conn:
            return conn.execute(
                "SELECT id FROM notifications WHERE recipient=? AND created_at > ?",
                (username, since)
            ).fetchall()

    async def event_generator():
        last_check = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        yield "data: connected\n\n"
        while True:
            try:
                await asyncio.sleep(3)
                rows = await asyncio.to_thread(_check_new, last_check)
                if rows:
                    last_check = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    yield "data: new\n\n"
                else:
                    yield ": keepalive\n\n"
            except asyncio.CancelledError:
                break
            except Exception:
                yield ": keepalive\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )
