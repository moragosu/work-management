from fastapi import APIRouter, Depends, HTTPException
from dependencies import get_current_user
import data_store
import re

router = APIRouter()


@router.get("")
def list_notifications(user: dict = Depends(get_current_user)):
    with data_store.get_conn() as conn:
        rows = conn.execute(
            "SELECT * FROM notifications WHERE recipient=? ORDER BY created_at DESC",
            (user["username"],)
        ).fetchall()
        notifications = [dict(r) for r in rows]
        # question_tagged 알림: 질문의 현재 답변 유무 확인 (답변 삭제 후에도 실시간 반영)
        qid_map = {}
        for n in notifications:
            if n["type"] == "question_tagged":
                m = re.search(r'focusQuestion=([^&]+)', n["link"] or "")
                if m:
                    qid_map[n["id"]] = m.group(1)
        answered = set()
        for nid, qid in qid_map.items():
            if conn.execute("SELECT 1 FROM answers WHERE question_id=?", (qid,)).fetchone():
                answered.add(nid)
        for n in notifications:
            n["is_pending"] = (n["id"] in qid_map and n["id"] not in answered)
    return notifications


@router.get("/unread-count")
def unread_count(user: dict = Depends(get_current_user)):
    with data_store.get_conn() as conn:
        row = conn.execute(
            "SELECT COUNT(*) as cnt FROM notifications WHERE recipient=? AND is_read=0",
            (user["username"],)
        ).fetchone()
    return {"count": row["cnt"]}


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
        # question_tagged 알림: 해당 질문에 답변이 없으면 삭제 불가
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
        conn.execute("DELETE FROM notifications WHERE id=?", (nid,))
    return {"ok": True}
