from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel
from datetime import datetime
import secrets
import string
import data_store
import auth_utils
from dependencies import get_current_user, require_admin
from utils.id_generator import short_uuid

router = APIRouter()


class SignupRequest(BaseModel):
    username: str
    name: str
    password: str


class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str


class RoleUpdate(BaseModel):
    role: str


class AdminUpdate(BaseModel):
    is_admin: bool


class StaffLinkUpdate(BaseModel):
    staff_id: str | None = None


@router.post("/login")
def login(form: OAuth2PasswordRequestForm = Depends()):
    with data_store.get_conn() as conn:
        row = conn.execute(
            "SELECT username, name, role, is_admin, force_password_change, password_hash FROM users WHERE username=?",
            (form.username,)
        ).fetchone()
    if not row or not auth_utils.verify_password(form.password, row["password_hash"]):
        raise HTTPException(status_code=401, detail="아이디 또는 비밀번호가 올바르지 않습니다")
    token = auth_utils.create_access_token({"sub": row["username"]})
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": {
            "username": row["username"],
            "name": row["name"],
            "role": row["role"],
            "is_admin": bool(row["is_admin"]),
            "force_password_change": bool(row["force_password_change"]),
        },
    }


@router.post("/signup", status_code=201)
def signup(body: SignupRequest):
    if not body.username.strip() or not body.name.strip() or not body.password:
        raise HTTPException(status_code=400, detail="모든 필드를 입력해주세요")
    with data_store.get_conn() as conn:
        exists = conn.execute("SELECT 1 FROM users WHERE username=?", (body.username,)).fetchone()
        if exists:
            raise HTTPException(status_code=409, detail="이미 사용 중인 아이디입니다")
        # staff 자동 생성·연결
        # user_id IS NULL인 staff만 검색 — 이미 다른 계정이 연결된 staff는 제외
        staff_matches = conn.execute(
            "SELECT id FROM staff WHERE name=? AND user_id IS NULL", (body.name.strip(),)
        ).fetchall()
        if len(staff_matches) == 1:
            # 이름 매칭 1개 → 기존 staff에 연결
            staff_id = staff_matches[0]["id"]
        elif len(staff_matches) == 0:
            # 매칭 없음(신규 또는 이미 연결된 동명) → 새 staff 생성
            staff_id = short_uuid("S")
            conn.execute("INSERT INTO staff (id, name, user_id) VALUES (?, ?, ?)",
                         (staff_id, body.name.strip(), body.username))
        else:
            # 동명이인 미연결 staff가 2개 이상 → 관리자가 수동 지정
            staff_id = None
        conn.execute(
            "INSERT INTO users (username, name, password_hash, role, is_admin, staff_id, created_at) VALUES (?,?,?,?,?,?,?)",
            (body.username, body.name, auth_utils.hash_password(body.password), "member", 0, staff_id, datetime.now().isoformat()),
        )
        # staff.user_id 동기화 (기존 staff에 연결된 경우)
        if staff_id and len(staff_matches) == 1:
            conn.execute("UPDATE staff SET user_id=? WHERE id=?", (body.username, staff_id))
    token = auth_utils.create_access_token({"sub": body.username})
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": {"username": body.username, "name": body.name, "role": "member", "is_admin": False, "force_password_change": False},
    }


@router.get("/me")
def me(user: dict = Depends(get_current_user)):
    return user


@router.put("/password")
def change_password(body: ChangePasswordRequest, user: dict = Depends(get_current_user)):
    with data_store.get_conn() as conn:
        row = conn.execute("SELECT password_hash FROM users WHERE username=?", (user["username"],)).fetchone()
        if not row or not auth_utils.verify_password(body.current_password, row["password_hash"]):
            raise HTTPException(status_code=400, detail="현재 비밀번호가 올바르지 않습니다")
        conn.execute(
            "UPDATE users SET password_hash=?, force_password_change=0 WHERE username=?",
            (auth_utils.hash_password(body.new_password), user["username"]),
        )
    return {"ok": True}


@router.get("/users")
def list_users(_admin: dict = Depends(require_admin)):
    with data_store.get_conn() as conn:
        rows = conn.execute(
            """SELECT u.username, u.name, u.role, u.is_admin, u.created_at, u.staff_id,
                      s.name AS staff_name
               FROM users u LEFT JOIN staff s ON u.staff_id = s.id
               ORDER BY u.created_at"""
        ).fetchall()
    return [dict(r) for r in rows]


@router.get("/qa-targets")
def get_qa_targets(_user: dict = Depends(get_current_user)):
    """Q&A 질문 대상: 그룹장·파트장 목록 반환 (파트원은 프론트에서 staff 목록 사용)."""
    with data_store.get_conn() as conn:
        rows = conn.execute(
            "SELECT username, name, role FROM users WHERE role IN ('group_leader', 'part_leader') ORDER BY name"
        ).fetchall()
    return [dict(r) for r in rows]


@router.get("/staff-unlinked")
def get_staff_unlinked(_admin: dict = Depends(require_admin)):
    """staff_id가 없는 staff 목록 반환 (Admin UI 연결 드롭다운용)."""
    with data_store.get_conn() as conn:
        linked_ids = [r["staff_id"] for r in conn.execute(
            "SELECT staff_id FROM users WHERE staff_id IS NOT NULL"
        ).fetchall()]
        rows = conn.execute("SELECT id, name, user_id FROM staff ORDER BY name").fetchall()
    all_staff = [dict(r) for r in rows]
    return all_staff


@router.put("/users/{username}/role")
def update_role(username: str, body: RoleUpdate, _admin: dict = Depends(require_admin)):
    if body.role not in ("member", "group_leader", "part_leader"):
        raise HTTPException(status_code=400, detail="유효하지 않은 직책입니다")
    with data_store.get_conn() as conn:
        user_row = conn.execute(
            "SELECT name, staff_id FROM users WHERE username=?", (username,)
        ).fetchone()
        if not user_row:
            raise HTTPException(status_code=404, detail="사용자를 찾을 수 없습니다")

        if body.role in ("group_leader", "part_leader"):
            result = conn.execute(
                "UPDATE users SET role=? WHERE username=?", (body.role, username)
            )
            # 리더로 변경 시 연결된 staff.user_id 초기화 (인력 탭 제외 처리용)
            if user_row["staff_id"]:
                conn.execute("UPDATE staff SET user_id=NULL WHERE id=?", (user_row["staff_id"],))
        else:
            # 파트원으로 변경 시 이름 기반 staff 자동 연결
            staff_id = user_row["staff_id"]
            if not staff_id:
                matches = conn.execute(
                    "SELECT id FROM staff WHERE name=? AND user_id IS NULL", (user_row["name"],)
                ).fetchall()
                if len(matches) == 1:
                    staff_id = matches[0]["id"]
            result = conn.execute(
                "UPDATE users SET role=?, staff_id=? WHERE username=?", (body.role, staff_id, username)
            )
            # staff.user_id 동기화
            if staff_id:
                conn.execute("UPDATE staff SET user_id=? WHERE id=?", (username, staff_id))
        if result.rowcount == 0:
            raise HTTPException(status_code=404, detail="사용자를 찾을 수 없습니다")
    return {"ok": True}


@router.put("/users/{username}/staff-link")
def update_staff_link(username: str, body: StaffLinkUpdate, _admin: dict = Depends(require_admin)):
    with data_store.get_conn() as conn:
        if body.staff_id is not None:
            if not conn.execute("SELECT 1 FROM staff WHERE id=?", (body.staff_id,)).fetchone():
                raise HTTPException(status_code=404, detail="해당 staff를 찾을 수 없습니다")
        result = conn.execute("UPDATE users SET staff_id=? WHERE username=?", (body.staff_id, username))
        if result.rowcount == 0:
            raise HTTPException(status_code=404, detail="사용자를 찾을 수 없습니다")
    return {"ok": True}


@router.post("/users/{username}/reset-password")
def reset_password(username: str, _admin: dict = Depends(require_admin)):
    with data_store.get_conn() as conn:
        row = conn.execute("SELECT username FROM users WHERE username=?", (username,)).fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="사용자를 찾을 수 없습니다")
        alphabet = string.ascii_letters + string.digits
        temp_pw = ''.join(secrets.choice(alphabet) for _ in range(10))
        conn.execute(
            "UPDATE users SET password_hash=?, force_password_change=1 WHERE username=?",
            (auth_utils.hash_password(temp_pw), username),
        )
    return {"temp_password": temp_pw}


@router.put("/users/{username}/admin")
def update_admin(username: str, body: AdminUpdate, admin: dict = Depends(require_admin)):
    if username == admin["username"] and not body.is_admin:
        raise HTTPException(status_code=400, detail="자신의 관리자 권한은 해제할 수 없습니다")
    with data_store.get_conn() as conn:
        result = conn.execute("UPDATE users SET is_admin=? WHERE username=?", (1 if body.is_admin else 0, username))
        if result.rowcount == 0:
            raise HTTPException(status_code=404, detail="사용자를 찾을 수 없습니다")
    return {"ok": True}


@router.delete("/users/{username}")
def delete_user(username: str, admin: dict = Depends(require_admin)):
    if username == admin["username"]:
        raise HTTPException(status_code=400, detail="자기 자신은 삭제할 수 없습니다")
    with data_store.get_conn() as conn:
        result = conn.execute("DELETE FROM users WHERE username=?", (username,))
        if result.rowcount == 0:
            raise HTTPException(status_code=404, detail="사용자를 찾을 수 없습니다")
    return {"ok": True}
