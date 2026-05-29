#!/usr/bin/env python3
"""
staff_accounts.json을 읽어 파트원 계정을 일괄 생성하는 스크립트.

개발:  cd backend && uv run python create_staff_accounts.py
prod:  sudo DATA_DIR=/var/www/okr-app/data \
           /var/www/okr-app/backend/.venv/bin/python \
           /var/www/okr-app/backend/create_staff_accounts.py
"""
import json
import os
import sqlite3
import sys
import argparse
from datetime import datetime
from pathlib import Path

import bcrypt

DATA_DIR = Path(os.environ.get("DATA_DIR", Path(__file__).parent.parent / "data"))
DB_PATH = DATA_DIR / "app.db"
MAPPING_FILE = Path(__file__).parent / "staff_accounts.json"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--force", action="store_true",
                        help="이미 존재하는 계정도 비밀번호와 force_password_change=1로 업데이트")
    args = parser.parse_args()

    if not DB_PATH.exists():
        print(f"DB 파일을 찾을 수 없습니다: {DB_PATH}")
        print("서버를 한 번 실행해 DB를 초기화한 뒤 다시 시도하세요.")
        sys.exit(1)

    if not MAPPING_FILE.exists():
        print(f"매핑 파일을 찾을 수 없습니다: {MAPPING_FILE}")
        sys.exit(1)

    with open(MAPPING_FILE, encoding="utf-8") as f:
        config = json.load(f)

    default_password = config.get("default_password", "")
    if not default_password:
        print("staff_accounts.json에 default_password가 비어 있습니다.")
        sys.exit(1)

    staff_list = config.get("staff", [])
    if not staff_list:
        print("staff_accounts.json에 staff 항목이 없습니다.")
        sys.exit(1)

    # username이 비어있는 항목 검사
    missing = [s["name"] for s in staff_list if not s.get("username", "").strip()]
    if missing:
        print("아래 인원의 username이 비어 있습니다. 채운 뒤 다시 실행하세요:")
        for name in missing:
            print(f"  - {name}")
        sys.exit(1)

    password_hash = bcrypt.hashpw(default_password.encode(), bcrypt.gensalt()).decode()

    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    try:
        created = []
        updated = []
        skipped = []

        for entry in staff_list:
            username = entry["username"].strip()
            name = entry["name"].strip()

            existing = conn.execute(
                "SELECT username FROM users WHERE username=? OR name=?", (username, name)
            ).fetchone()

            if existing:
                if args.force:
                    conn.execute(
                        "UPDATE users SET password_hash=?, force_password_change=1 WHERE username=?",
                        (password_hash, existing["username"]),
                    )
                    updated.append(f"{name} ({existing['username']})")
                else:
                    skipped.append(f"{name} ({username}) — 이미 존재: {existing['username']}")
                continue

            conn.execute(
                "INSERT INTO users (username, name, password_hash, role, force_password_change, created_at) VALUES (?,?,?,?,?,?)",
                (username, name, password_hash, "member", 1, datetime.now().isoformat()),
            )
            created.append(f"{name} ({username})")

        conn.commit()
    finally:
        conn.close()

    print(f"\n=== 결과 ===")
    print(f"초기 비밀번호: {default_password}")
    print()
    if created:
        print(f"✅ 생성 완료 ({len(created)}명):")
        for line in created:
            print(f"   {line}")
    if updated:
        print(f"\n🔄 업데이트 완료 ({len(updated)}명) — 비밀번호 초기화 + 변경 강제:")
        for line in updated:
            print(f"   {line}")
    if skipped:
        print(f"\n⏭  건너뜀 ({len(skipped)}명):")
        for line in skipped:
            print(f"   {line}")
    if not created and not updated:
        print("변경된 계정이 없습니다. 기존 계정을 초기화하려면 --force 옵션을 사용하세요.")


if __name__ == "__main__":
    main()
