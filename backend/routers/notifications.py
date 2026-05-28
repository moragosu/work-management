from fastapi import APIRouter, Depends
from dependencies import get_current_user
import data_store

router = APIRouter()


@router.get("")
def list_notifications(user: dict = Depends(get_current_user)):
    with data_store.get_conn() as conn:
        rows = conn.execute(
            "SELECT * FROM notifications WHERE recipient=? ORDER BY created_at DESC LIMIT 50",
            (user["username"],)
        ).fetchall()
    return [dict(r) for r in rows]


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
        conn.execute(
            "DELETE FROM notifications WHERE id=? AND recipient=?",
            (nid, user["username"])
        )
    return {"ok": True}
