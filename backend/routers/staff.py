import json
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import List, Optional
import data_store

router = APIRouter()


class StaffMember(BaseModel):
    username: str
    name: str
    job_title: str = ""
    main_skills: str = ""
    sub_skills: str = ""
    learning: str = ""
    desired_field: str = ""
    okrs: str = ""
    task_ids: List[str] = []
    user_id: Optional[str] = None  # backward compat — username과 동일


class StaffUpdate(BaseModel):
    name: Optional[str] = None
    job_title: Optional[str] = None
    main_skills: Optional[str] = None
    sub_skills: Optional[str] = None
    learning: Optional[str] = None
    desired_field: Optional[str] = None
    okrs: Optional[str] = None
    task_ids: Optional[List[str]] = None


def _row_to_member(row) -> dict:
    d = dict(row)
    if isinstance(d.get("task_ids"), str):
        try:
            d["task_ids"] = json.loads(d["task_ids"])
        except (json.JSONDecodeError, TypeError):
            d["task_ids"] = []
    d["user_id"] = d.get("username")
    return d


@router.get("", response_model=List[StaffMember])
def list_staff(search: Optional[str] = Query(None)):
    with data_store.get_conn() as conn:
        rows = conn.execute(
            """SELECT username, name, job_title, main_skills, sub_skills,
                      learning, desired_field, okrs, task_ids
               FROM users WHERE role = 'member' ORDER BY name"""
        ).fetchall()
    staff = [_row_to_member(r) for r in rows]

    if search:
        q = search.lower()
        staff = [
            s for s in staff
            if q in s["name"].lower()
            or q in s["main_skills"].lower()
            or q in s["sub_skills"].lower()
            or q in s["learning"].lower()
            or q in s["okrs"].lower()
        ]
    return staff


@router.get("/{username}", response_model=StaffMember)
def get_staff(username: str):
    with data_store.get_conn() as conn:
        row = conn.execute(
            """SELECT username, name, job_title, main_skills, sub_skills,
                      learning, desired_field, okrs, task_ids
               FROM users WHERE username=? AND role='member'""",
            (username,)
        ).fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Staff member not found")
    return _row_to_member(row)


@router.post("", response_model=StaffMember, status_code=201)
def create_staff(member: StaffMember):
    """관리자가 직접 파트원 계정 없이 인력 정보를 등록할 때 사용."""
    import secrets, string
    from utils.id_generator import short_uuid
    import auth_utils
    username = member.username or short_uuid("U")
    task_ids_json = json.dumps(member.task_ids or [], ensure_ascii=False)
    with data_store.get_conn() as conn:
        if conn.execute("SELECT 1 FROM users WHERE username=?", (username,)).fetchone():
            raise HTTPException(status_code=409, detail="이미 존재하는 아이디입니다")
        temp_pw = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(10))
        conn.execute(
            """INSERT INTO users
               (username, name, password_hash, role, is_admin, force_password_change,
                job_title, main_skills, sub_skills, learning, desired_field, okrs, task_ids, created_at)
               VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
            (username, member.name, auth_utils.hash_password(temp_pw),
             "member", 0, 1,
             member.job_title, member.main_skills, member.sub_skills,
             member.learning, member.desired_field, member.okrs, task_ids_json,
             __import__('datetime').datetime.now().isoformat())
        )
    return get_staff(username)


@router.put("/{username}", response_model=StaffMember)
def update_staff(username: str, update: StaffUpdate):
    patch = update.model_dump(exclude_none=True)
    if "task_ids" in patch:
        patch["task_ids"] = json.dumps(patch["task_ids"], ensure_ascii=False)
    if not patch:
        return get_staff(username)
    sets = ", ".join(f"{k}=?" for k in patch)
    values = list(patch.values()) + [username]
    with data_store.get_conn() as conn:
        result = conn.execute(
            f"UPDATE users SET {sets} WHERE username=? AND role='member'", values
        )
        if result.rowcount == 0:
            raise HTTPException(status_code=404, detail="Staff member not found")
    return get_staff(username)


@router.delete("/{username}")
def delete_staff(username: str):
    with data_store.get_conn() as conn:
        result = conn.execute(
            "DELETE FROM users WHERE username=? AND role='member'", (username,)
        )
        if result.rowcount == 0:
            raise HTTPException(status_code=404, detail="Staff member not found")
    return {"deleted": username}
