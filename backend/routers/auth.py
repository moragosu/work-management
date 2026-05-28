from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel
from datetime import datetime
import data_store
import auth_utils
from dependencies import get_current_user, require_admin

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


@router.post("/login")
def login(form: OAuth2PasswordRequestForm = Depends()):
    with data_store.get_conn() as conn:
        row = conn.execute(
            "SELECT username, name, role, password_hash FROM users WHERE username=?",
            (form.username,)
        ).fetchone()
    if not row or not auth_utils.verify_password(form.password, row["password_hash"]):
        raise HTTPException(status_code=401, detail="아이디 또는 비밀번호가 올바르지 않습니다")
    token = auth_utils.create_access_token({"sub": row["username"]})
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": {"username": row["username"], "name": row["name"], "role": row["role"]},
    }


@router.post("/signup", status_code=201)
def signup(body: SignupRequest):
    if not body.username.strip() or not body.name.strip() or not body.password:
        raise HTTPException(status_code=400, detail="모든 필드를 입력해주세요")
    with data_store.get_conn() as conn:
        exists = conn.execute("SELECT 1 FROM users WHERE username=?", (body.username,)).fetchone()
        if exists:
            raise HTTPException(status_code=409, detail="이미 사용 중인 아이디입니다")
        conn.execute(
            "INSERT INTO users (username, name, password_hash, role, created_at) VALUES (?,?,?,?,?)",
            (body.username, body.name, auth_utils.hash_password(body.password), "member", datetime.now().isoformat()),
        )
    token = auth_utils.create_access_token({"sub": body.username})
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": {"username": body.username, "name": body.name, "role": "member"},
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
            "UPDATE users SET password_hash=? WHERE username=?",
            (auth_utils.hash_password(body.new_password), user["username"]),
        )
    return {"ok": True}


@router.get("/users")
def list_users(_admin: dict = Depends(require_admin)):
    with data_store.get_conn() as conn:
        rows = conn.execute("SELECT username, name, role, created_at FROM users ORDER BY created_at").fetchall()
    return [dict(r) for r in rows]


@router.put("/users/{username}/role")
def update_role(username: str, body: RoleUpdate, _admin: dict = Depends(require_admin)):
    if body.role not in ("member", "group_leader", "part_leader", "admin"):
        raise HTTPException(status_code=400, detail="유효하지 않은 역할입니다")
    with data_store.get_conn() as conn:
        result = conn.execute("UPDATE users SET role=? WHERE username=?", (body.role, username))
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
