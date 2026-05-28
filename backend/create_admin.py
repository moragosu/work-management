#!/usr/bin/env python3
"""
초기 admin 계정 생성 스크립트.

개발:  python create_admin.py
prod:  sudo DATA_DIR=/var/www/okr-app/data \
           /var/www/okr-app/backend/.venv/bin/python create_admin.py
"""
import os
import sys
import getpass
import sqlite3
import bcrypt
from pathlib import Path
from datetime import datetime

DATA_DIR = Path(os.environ.get("DATA_DIR", Path(__file__).parent.parent / "data"))
DB_PATH = DATA_DIR / "app.db"


def main():
    if not DB_PATH.exists():
        print(f"DB 파일을 찾을 수 없습니다: {DB_PATH}")
        print("서버를 한 번 실행해 DB를 초기화한 뒤 다시 시도하세요.")
        sys.exit(1)

    print("=== admin 계정 생성 ===")
    username = input("username (기본값: admin): ").strip() or "admin"
    name     = input("표시 이름 (기본값: 관리자): ").strip() or "관리자"

    while True:
        password = getpass.getpass("비밀번호: ")
        if len(password) < 6:
            print("비밀번호는 6자 이상이어야 합니다.")
            continue
        confirm = getpass.getpass("비밀번호 확인: ")
        if password != confirm:
            print("비밀번호가 일치하지 않습니다.")
            continue
        break

    password_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

    conn = sqlite3.connect(str(DB_PATH))
    try:
        existing = conn.execute("SELECT role FROM users WHERE username=?", (username,)).fetchone()
        if existing:
            answer = input(f"'{username}' 계정이 이미 존재합니다 (현재 role: {existing[0]}). 덮어쓰시겠습니까? [y/N] ")
            if answer.strip().lower() != "y":
                print("취소했습니다.")
                sys.exit(0)
            conn.execute(
                "UPDATE users SET name=?, password_hash=?, is_admin=1 WHERE username=?",
                (name, password_hash, username),
            )
            print(f"✅ '{username}' 계정에 관리자 권한을 부여했습니다.")
        else:
            conn.execute(
                "INSERT INTO users (username, name, password_hash, role, is_admin, created_at) VALUES (?,?,?,?,?,?)",
                (username, name, password_hash, "member", 1, datetime.now().isoformat()),
            )
            print(f"✅ admin 계정 '{username}' 생성 완료.")
        conn.commit()
    finally:
        conn.close()


if __name__ == "__main__":
    main()
