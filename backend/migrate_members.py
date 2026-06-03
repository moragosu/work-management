"""
마이그레이션: staff.selected_tasks → tasks.members / sub_tasks[].members

기존 DB는 직원(staff) 레코드의 selected_tasks 컬럼(쉼표 구분 문자열)에
과제 배정 정보를 저장했습니다. OKR 현황 탭은 tasks.members(JSON 배열)를
읽으므로, 두 방향의 데이터를 일치시킵니다.

실행:
    DATA_DIR=../data uv run python migrate_members.py
    또는
    DATA_DIR=/path/to/data python migrate_members.py
"""

import json
import sys
import os

# DATA_DIR 환경변수를 data_store가 읽을 수 있도록 설정
if "DATA_DIR" not in os.environ:
    os.environ["DATA_DIR"] = os.path.join(os.path.dirname(__file__), "..", "data")

from data_store import get_conn


def run():
    conn = get_conn()

    # 1. staff 레코드에서 selected_tasks 파싱
    staff_rows = conn.execute(
        "SELECT id, name, role, selected_tasks, user_id FROM staff"
    ).fetchall()

    task_to_members: dict[str, list] = {}
    subtask_to_members: dict[str, list] = {}

    for row in staff_rows:
        d = dict(row)
        raw = (d.get("selected_tasks") or "").strip()
        if not raw:
            continue
        member = {
            "username": d["user_id"] or "",
            "name": d["name"] or "",
            "role": d["role"] or "",
        }
        for tid in [t.strip() for t in raw.split(",") if t.strip()]:
            if "-" in tid:
                subtask_to_members.setdefault(tid, []).append(member)
            else:
                task_to_members.setdefault(tid, []).append(member)

    # 2. tasks 테이블 업데이트
    tasks = conn.execute("SELECT id, members, sub_tasks FROM tasks").fetchall()
    updated = skipped = 0

    for row in tasks:
        d = dict(row)
        tid = d["id"]

        new_members = task_to_members.get(tid, [])

        sub_tasks = json.loads(d["sub_tasks"] or "[]")
        for st in sub_tasks:
            st_members = subtask_to_members.get(st["id"], [])
            if st_members:
                st["members"] = st_members
            elif "members" not in st:
                st["members"] = []

        existing = json.loads(d["members"] or "[]")
        if existing and not new_members:
            # 이미 members가 있고 selected_tasks에 없으면 덮어쓰지 않음
            skipped += 1
            continue

        conn.execute(
            "UPDATE tasks SET members=?, sub_tasks=? WHERE id=?",
            (
                json.dumps(new_members, ensure_ascii=False),
                json.dumps(sub_tasks, ensure_ascii=False),
                tid,
            ),
        )
        updated += 1

    conn.commit()
    print(f"완료: {updated}개 과제 업데이트, {skipped}개 건너뜀 (이미 members 존재)")

    # 3. 결과 요약 출력
    print("\n[과제별 담당자 요약]")
    for tid, members in sorted(task_to_members.items()):
        names = ", ".join(m["name"] for m in members)
        print(f"  {tid}: {names}")
    if subtask_to_members:
        print("\n[소과제별 담당자 요약]")
        for tid, members in sorted(subtask_to_members.items()):
            names = ", ".join(m["name"] for m in members)
            print(f"  {tid}: {names}")


if __name__ == "__main__":
    run()
