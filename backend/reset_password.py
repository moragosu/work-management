#!/usr/bin/env python3
"""
특정 사용자의 비밀번호를 재설정하는 스크립트 (관리자 전용).

개발:  cd backend && uv run python reset_password.py
prod:  sudo DATA_DIR=/var/www/okr-app/data \
           /var/www/okr-app/backend/.venv/bin/python \
           /var/www/okr-app/backend/reset_password.py
"""
import os
import sys
import getpass
import sqlite3
from pathlib import Path

import bcrypt

DATA_DIR = Path(os.environ.get("DATA_DIR", Path(__file__).parent.parent / "data"))
DB_PATH = DATA_DIR / "app.db"


def main():
    if not DB_PATH.exists():
        print(f"DB 파일을 찾을 수 없습니다: {DB_PATH}")
        sys.exit(1)

    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row

    rows = conn.execute("SELECT username, name, role, is_admin FROM users ORDER BY created_at").fetchall()
    if not rows:
        print("등록된 사용자가 없습니다.")
        sys.exit(0)

    print("=== 사용자 목록 ===")
    for r in rows:
        admin_tag = " [관리자]" if r["is_admin"] else ""
        role_map = {"member": "파트원", "group_leader": "그룹장", "part_leader": "파트장"}
        role_label = role_map.get(r["role"], r["role"])
        print(f"  {r['username']:<20} {r['name']:<10} {role_label}{admin_tag}")

    print()
    username = input("비밀번호를 재설정할 username: ").strip()
    if not username:
        print("취소했습니다.")
        sys.exit(0)

    target = conn.execute("SELECT username, name FROM users WHERE username=?", (username,)).fetchone()
    if not target:
        print(f"'{username}' 사용자를 찾을 수 없습니다.")
        sys.exit(1)

    print(f"대상: {target['name']} ({target['username']})")

    while True:
        password = getpass.getpass("새 비밀번호: ")
        if len(password) < 6:
            print("비밀번호는 6자 이상이어야 합니다.")
            continue
        confirm = getpass.getpass("새 비밀번호 확인: ")
        if password != confirm:
            print("비밀번호가 일치하지 않습니다.")
            continue
        break

    password_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
    conn.execute("UPDATE users SET password_hash=? WHERE username=?", (password_hash, username))
    conn.commit()
    conn.close()

    print(f"✅ '{target['name']}' 비밀번호가 재설정되었습니다.")


if __name__ == "__main__":
    main()
