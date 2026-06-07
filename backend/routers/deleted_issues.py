from fastapi import APIRouter, HTTPException, Depends, Query
from typing import Optional
import json
import data_store
from dependencies import get_current_user, require_admin

router = APIRouter()


def _serialize(row: dict) -> dict:
    row = dict(row)
    if isinstance(row.get("comments_snapshot"), str):
        try:
            row["comments_snapshot"] = json.loads(row["comments_snapshot"])
        except Exception:
            row["comments_snapshot"] = []
    return row


@router.get("")
def list_deleted_issues(
    week: Optional[str] = Query(None),
    task_id: Optional[str] = Query(None),
    user: dict = Depends(get_current_user),
):
    if not user.get("is_admin") and user.get("role") not in ("group_leader", "part_leader"):
        raise HTTPException(status_code=403, detail="파트장 이상만 조회할 수 있습니다")
    with data_store.get_conn() as conn:
        sql = "SELECT * FROM deleted_issues"
        params = []
        conditions = []
        if week:
            conditions.append("week=?")
            params.append(week)
        if task_id:
            conditions.append("task_id=?")
            params.append(task_id)
        if conditions:
            sql += " WHERE " + " AND ".join(conditions)
        sql += " ORDER BY deleted_at DESC"
        rows = conn.execute(sql, params).fetchall()
    return [_serialize(dict(r)) for r in rows]


@router.delete("/{record_id}")
def permanently_delete(record_id: str, user: dict = Depends(require_admin)):
    with data_store.get_conn() as conn:
        row = conn.execute("SELECT id FROM deleted_issues WHERE id=?", (record_id,)).fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="기록을 찾을 수 없습니다")
        conn.execute("DELETE FROM deleted_issues WHERE id=?", (record_id,))
    return {"deleted": record_id}
