#!/usr/bin/env python3
"""
단일 사용자 계정 생성 스크립트.

사용법:
  DATA_DIR=../data uv run python create_user.py --username hong.gildong --name 홍길동 --password 초기비번123
  DATA_DIR=../data uv run python create_user.py --username kim.cs --name 김철수 --role group_leader --password 초기비번123
  DATA_DIR=../data uv run python create_user.py --username admin2 --name 관리자2 --admin --password 초기비번123
  DATA_DIR=../data uv run python create_user.py --username hong.gildong --name 홍길동 --password 새비번 --force

옵션:
  --username   로그인 ID (필수)
  --name       표시 이름 (필수)
  --password   초기 비밀번호 (필수)
  --role       member(기본) / group_leader / part_leader
  --admin      관리자 권한 부여 (is_admin=1)
  --force      이미 존재하는 계정 덮어쓰기
"""
import argparse
import os
import sys
import sqlite3
from datetime import datetime
from pathlib import Path

import bcrypt

DATA_DIR = Path(os.environ.get("DATA_DIR", Path(__file__).parent.parent / "data"))
DB_PATH = DATA_DIR / "app.db"

VALID_ROLES = {"member", "group_leader", "part_leader"}


def parse_args():
    p = argparse.ArgumentParser(description="사용자 계정 생성")
    p.add_argument("--username", required=True, help="로그인 ID")
    p.add_argument("--name",     required=True, help="표시 이름")
    p.add_argument("--password", required=True, help="초기 비밀번호")
    p.add_argument("--role",     default="member", choices=sorted(VALID_ROLES), help="역할 (기본: member)")
    p.add_argument("--admin",    action="store_true", help="관리자 권한 부여")
    p.add_argument("--force",    action="store_true", help="기존 계정 덮어쓰기")
    return p.parse_args()


def main():
    args = parse_args()

    if not DB_PATH.exists():
        print(f"[오류] DB 파일을 찾을 수 없습니다: {DB_PATH}")
        print("       서버를 한 번 실행해 DB를 초기화한 뒤 다시 시도하세요.")
        sys.exit(1)

    if len(args.password) < 4:
        print("[오류] 비밀번호는 4자 이상이어야 합니다.")
        sys.exit(1)

    password_hash = bcrypt.hashpw(args.password.encode(), bcrypt.gensalt()).decode()
    is_admin = 1 if args.admin else 0
    now = datetime.now().isoformat()

    conn = sqlite3.connect(str(DB_PATH))
    try:
        existing = conn.execute(
            "SELECT username, role, is_admin FROM users WHERE username=?", (args.username,)
        ).fetchone()

        if existing and not args.force:
            print(f"[오류] '{args.username}' 계정이 이미 존재합니다.")
            print("       덮어쓰려면 --force 옵션을 추가하세요.")
            sys.exit(1)

        if existing:
            conn.execute(
                """UPDATE users
                   SET name=?, password_hash=?, role=?, is_admin=?,
                       force_password_change=1
                   WHERE username=?""",
                (args.name, password_hash, args.role, is_admin, args.username),
            )
            action = "업데이트"
        else:
            conn.execute(
                """INSERT INTO users
                   (username, name, password_hash, role, is_admin, force_password_change, created_at)
                   VALUES (?,?,?,?,?,?,?)""",
                (args.username, args.name, password_hash, args.role, is_admin, 1, now),
            )
            action = "생성"

        # staff 테이블에 같은 이름이 있으면 자동 연결
        staff = conn.execute(
            "SELECT id FROM staff WHERE name=?", (args.name,)
        ).fetchone()
        if staff:
            conn.execute(
                "UPDATE users SET staff_id=? WHERE username=?",
                (staff[0], args.username),
            )
            conn.execute(
                "UPDATE staff SET user_id=? WHERE id=?",
                (args.username, staff[0]),
            )

        conn.commit()

        role_label = {"member": "파트원", "group_leader": "그룹장", "part_leader": "파트장"}.get(args.role, args.role)
        admin_label = " (관리자)" if is_admin else ""
        staff_label = f"  → staff 연결: {staff[0]}" if staff else ""
        print(f"✅ '{args.username}' ({args.name}) 계정 {action} 완료.")
        print(f"   역할: {role_label}{admin_label}")
        print(f"   첫 로그인 시 비밀번호 변경이 강제됩니다.{staff_label}")

    finally:
        conn.close()


if __name__ == "__main__":
    main()
