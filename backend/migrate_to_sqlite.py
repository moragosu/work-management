#!/usr/bin/env python3
"""
JSON → SQLite 마이그레이션 스크립트

사용법:
  개발:  python migrate_to_sqlite.py
  운영:  DATA_DIR=/var/www/okr-app/data python migrate_to_sqlite.py
  강제:  python migrate_to_sqlite.py --force   (기존 app.db 덮어쓰기)

동작:
  1. DATA_DIR의 기존 JSON 파일 읽기
  2. DATA_DIR/app.db 생성 + 테이블 초기화
  3. 각 JSON 데이터 → SQLite 테이블에 INSERT
  4. 기존 JSON 파일을 DATA_DIR/json_backup/ 로 이동 (안전 보관)
  5. 결과 요약 출력
"""

import sys
import json
import shutil
from pathlib import Path
from datetime import datetime

# ── 환경 설정 ─────────────────────────────────────────────────────────────────

import os
os.environ.setdefault("DATA_DIR", str(Path(__file__).parent.parent / "data"))

import data_store

DATA_DIR = data_store.DATA_DIR
DB_PATH  = data_store.DB_PATH
BACKUP_DIR = DATA_DIR / "json_backup"

FORCE = "--force" in sys.argv

# ── JSON 파일 목록 ────────────────────────────────────────────────────────────

JSON_FILES = [
    "okrs.json",
    "tasks.json",
    "progress.json",
    "staff.json",
    "qna.json",
    "issues.json",
    "feedback.json",
    "confluence_links.json",
    "settings.json",
    "id_counters.json",
]


def load_json(filename: str):
    path = DATA_DIR / filename
    if not path.exists():
        return None
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def count_items(data, filename: str) -> int:
    if data is None:
        return 0
    if filename == "qna.json":
        return len(data.get("questions", [])) + len(data.get("answers", []))
    if filename in ("settings.json", "id_counters.json"):
        return len(data)
    # 일반 테이블: 첫 번째 값의 길이
    for v in data.values():
        if isinstance(v, list):
            return len(v)
    return 0


def backup_json_files(migrated: list[str]):
    if not migrated:
        return
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    for filename in migrated:
        src = DATA_DIR / filename
        if src.exists():
            dst = BACKUP_DIR / f"{src.stem}_{timestamp}{src.suffix}"
            shutil.move(str(src), str(dst))
            print(f"  백업: {filename} → json_backup/{dst.name}")


def main():
    print("=" * 55)
    print("  JSON → SQLite 마이그레이션")
    print(f"  DATA_DIR: {DATA_DIR}")
    print(f"  DB 경로:  {DB_PATH}")
    print("=" * 55)

    # ── DB 파일 존재 여부 확인 ──────────────────────────────────────────────
    if DB_PATH.exists() and not FORCE:
        print(f"\n⚠️  이미 app.db 가 존재합니다.")
        print("   기존 DB를 유지하려면 그냥 종료하세요.")
        print("   덮어쓰려면: python migrate_to_sqlite.py --force\n")
        sys.exit(1)

    if DB_PATH.exists() and FORCE:
        DB_PATH.unlink()
        print("  기존 app.db 삭제 후 재생성합니다.\n")

    # ── 테이블 초기화 ───────────────────────────────────────────────────────
    print("[1/3] 테이블 초기화...")
    data_store.init_db()
    print("  완료\n")

    # ── JSON 읽기 → SQLite 저장 ─────────────────────────────────────────────
    print("[2/3] 데이터 마이그레이션...")
    migrated = []
    total = 0

    for filename in JSON_FILES:
        data = load_json(filename)
        if data is None:
            print(f"  건너뜀: {filename} (파일 없음)")
            continue

        cnt = count_items(data, filename)
        data_store.save(filename, data)
        print(f"  ✅ {filename:30s} → {cnt}건")
        migrated.append(filename)
        total += cnt

    print(f"\n  총 {total}건 마이그레이션 완료\n")

    # ── JSON 백업 ───────────────────────────────────────────────────────────
    print("[3/3] 기존 JSON 파일 백업...")
    backup_json_files(migrated)

    print("\n" + "=" * 55)
    print(f"  ✅ 마이그레이션 완료!")
    print(f"  DB:     {DB_PATH}")
    print(f"  백업:   {BACKUP_DIR}")
    print("=" * 55)
    print()
    print("  다음 단계:")
    print("  개발) uv run uvicorn main:app --reload")
    print("  운영) sudo systemctl restart okr-app")
    print()


if __name__ == "__main__":
    main()
