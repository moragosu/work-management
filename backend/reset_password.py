#!/usr/bin/env python3
"""
사용자 비밀번호를 임시 비밀번호로 재설정하는 스크립트 (관리자 전용).

워크플로우:
  1. 관리자가 이 스크립트로 임시 비밀번호 설정
  2. 사용자에게 임시 비밀번호 전달
  3. 사용자가 로그인 후 직접 비밀번호 변경

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


def print_users(conn):
    rows = conn.execute("SELECT username, name, role, is_admin FROM users ORDER BY created_at").fetchall()
    role_map = {"member": "파트원", "group_leader": "그룹장", "part_leader": "파트장"}
    print("\n=== 사용자 목록 ===")
    for r in rows:
        admin_tag = " [관리자]" if r["is_admin"] else ""
        role_label = role_map.get(r["role"], r["role"])
        print(f"  {r['username']:<20} {r['name']:<10} {role_label}{admin_tag}")
    print()


def main():
    if not DB_PATH.exists():
        print(f"DB 파일을 찾을 수 없습니다: {DB_PATH}")
        sys.exit(1)

    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row

    # 임시 비밀번호 한 번만 입력
    print("=== 비밀번호 재설정 ===")
    while True:
        default_pw = getpass.getpass("임시 비밀번호 (사용자에게 전달할 비밀번호): ")
        if len(default_pw) < 6:
            print("비밀번호는 6자 이상이어야 합니다.")
            continue
        break

    password_hash = bcrypt.hashpw(default_pw.encode(), bcrypt.gensalt()).decode()

    # 연속 처리 루프
    while True:
        print_users(conn)
        username = input("재설정할 username (종료: Enter): ").strip()
        if not username:
            print("종료합니다.")
            break

        target = conn.execute("SELECT username, name FROM users WHERE username=?", (username,)).fetchone()
        if not target:
            print(f"  ❌ '{username}' 사용자를 찾을 수 없습니다.")
            continue

        conn.execute("UPDATE users SET password_hash=? WHERE username=?", (password_hash, username))
        conn.commit()
        print(f"  ✅ '{target['name']}' ({username}) 비밀번호가 임시 비밀번호로 재설정되었습니다.")
        print(f"     → 임시 비밀번호를 전달하고 로그인 후 변경하도록 안내하세요.\n")

    conn.close()


if __name__ == "__main__":
    main()
