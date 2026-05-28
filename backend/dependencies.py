from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
import data_store
import auth_utils

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


def get_current_user(token: str = Depends(oauth2_scheme)) -> dict:
    payload = auth_utils.decode_token(token)
    if not payload or "sub" not in payload:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="인증이 필요합니다")
    with data_store.get_conn() as conn:
        row = conn.execute("SELECT username, name, role FROM users WHERE username=?", (payload["sub"],)).fetchone()
    if not row:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="사용자를 찾을 수 없습니다")
    return dict(row)


def require_leader(user: dict = Depends(get_current_user)) -> dict:
    if user["role"] not in ("group_leader", "part_leader", "admin"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="리더 이상 권한이 필요합니다")
    return user


def require_admin(user: dict = Depends(get_current_user)) -> dict:
    if user["role"] != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="관리자 권한이 필요합니다")
    return user
