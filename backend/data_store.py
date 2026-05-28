"""
data_store.py — SQLite 기반 데이터 저장소
기존 load(filename) / save(filename, data) 인터페이스를 유지하여
라우터 코드 변경 없이 JSON → SQLite 전환.
"""
import json
import sqlite3
import os
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any

DATA_DIR = Path(os.environ.get("DATA_DIR", "/home/user/work-management/data"))
DB_PATH = DATA_DIR / "app.db"

# ── 스키마 정의 ───────────────────────────────────────────────────────────────

SCHEMA = """
CREATE TABLE IF NOT EXISTS objectives (
    id          TEXT PRIMARY KEY,
    name        TEXT NOT NULL DEFAULT '',
    tech_stack  TEXT NOT NULL DEFAULT '',
    status      TEXT NOT NULL DEFAULT '진행중',
    key_results TEXT NOT NULL DEFAULT '[]'
);
CREATE TABLE IF NOT EXISTS tasks (
    id           TEXT PRIMARY KEY,
    name         TEXT NOT NULL DEFAULT '',
    objective_id TEXT NOT NULL DEFAULT '',
    target       TEXT NOT NULL DEFAULT '',
    members      TEXT NOT NULL DEFAULT '[]',
    sub_tasks    TEXT NOT NULL DEFAULT '[]'
);
CREATE TABLE IF NOT EXISTS progress_items (
    id               TEXT PRIMARY KEY,
    week             TEXT NOT NULL DEFAULT '',
    objective        TEXT NOT NULL DEFAULT '',
    task_id          TEXT NOT NULL DEFAULT '',
    task_name        TEXT NOT NULL DEFAULT '',
    subtask          TEXT NOT NULL DEFAULT '',
    planned          TEXT NOT NULL DEFAULT '',
    result           TEXT NOT NULL DEFAULT '',
    progress_percent INTEGER NOT NULL DEFAULT 0,
    issue            TEXT NOT NULL DEFAULT '',
    assignee         TEXT NOT NULL DEFAULT '',
    solution         TEXT NOT NULL DEFAULT '',
    images           TEXT NOT NULL DEFAULT '[]',
    created_at       TEXT,
    updated_at       TEXT
);
CREATE TABLE IF NOT EXISTS staff (
    id             TEXT PRIMARY KEY,
    name           TEXT NOT NULL DEFAULT '',
    role           TEXT NOT NULL DEFAULT '',
    main_skills    TEXT NOT NULL DEFAULT '',
    sub_skills     TEXT NOT NULL DEFAULT '',
    learning       TEXT NOT NULL DEFAULT '',
    desired_field  TEXT NOT NULL DEFAULT '',
    okrs           TEXT NOT NULL DEFAULT '',
    selected_tasks TEXT NOT NULL DEFAULT '',
    task_ids       TEXT NOT NULL DEFAULT '[]'
);
CREATE TABLE IF NOT EXISTS questions (
    id         TEXT PRIMARY KEY,
    task_id    TEXT NOT NULL DEFAULT '',
    week       TEXT NOT NULL DEFAULT '',
    question   TEXT NOT NULL DEFAULT '',
    targets    TEXT NOT NULL DEFAULT '[]',
    questioner TEXT NOT NULL DEFAULT '',
    created_by TEXT NOT NULL DEFAULT '',
    created_at TEXT
);
CREATE TABLE IF NOT EXISTS answers (
    id          TEXT PRIMARY KEY,
    question_id TEXT NOT NULL DEFAULT '',
    answer      TEXT NOT NULL DEFAULT '',
    answer_by   TEXT NOT NULL DEFAULT '',
    images      TEXT NOT NULL DEFAULT '[]',
    created_at  TEXT,
    updated_at  TEXT
);
CREATE TABLE IF NOT EXISTS issues (
    id         TEXT PRIMARY KEY,
    task_id    TEXT NOT NULL DEFAULT '',
    week       TEXT NOT NULL DEFAULT '',
    issue      TEXT NOT NULL DEFAULT '',
    assignee   TEXT NOT NULL DEFAULT '',
    created_by TEXT NOT NULL DEFAULT '',
    created_at TEXT,
    updated_at TEXT
);
CREATE TABLE IF NOT EXISTS feedbacks (
    id         TEXT PRIMARY KEY,
    category   TEXT NOT NULL DEFAULT '',
    title      TEXT NOT NULL DEFAULT '',
    content    TEXT NOT NULL DEFAULT '',
    author     TEXT NOT NULL DEFAULT '',
    created_at TEXT,
    updated_at TEXT
);
CREATE TABLE IF NOT EXISTS confluence_links (
    id      TEXT PRIMARY KEY,
    week    TEXT NOT NULL DEFAULT '',
    task_id TEXT,
    url     TEXT NOT NULL DEFAULT ''
);
CREATE TABLE IF NOT EXISTS settings (
    key   TEXT PRIMARY KEY,
    value TEXT NOT NULL DEFAULT ''
);
CREATE TABLE IF NOT EXISTS id_counters (
    prefix TEXT PRIMARY KEY,
    value  INTEGER NOT NULL DEFAULT 0
);
CREATE TABLE IF NOT EXISTS notifications (
    id         TEXT PRIMARY KEY,
    recipient  TEXT NOT NULL DEFAULT '',
    type       TEXT NOT NULL DEFAULT '',
    title      TEXT NOT NULL DEFAULT '',
    message    TEXT NOT NULL DEFAULT '',
    link       TEXT NOT NULL DEFAULT '',
    is_read    INTEGER NOT NULL DEFAULT 0,
    created_at TEXT
);
CREATE TABLE IF NOT EXISTS users (
    username      TEXT PRIMARY KEY,
    name          TEXT NOT NULL DEFAULT '',
    password_hash TEXT NOT NULL DEFAULT '',
    role          TEXT NOT NULL DEFAULT 'member',
    created_at    TEXT
);
"""

# ── JSON 직렬화 컬럼 목록 (테이블별) ─────────────────────────────────────────

JSON_COLS = {
    "objectives":      {"key_results"},
    "tasks":           {"members", "sub_tasks"},
    "progress_items":  {"images"},
    "staff":           {"task_ids"},
    "questions":       {"targets"},
    "answers":         {"images"},
    "issues":          set(),
    "feedbacks":       set(),
    "confluence_links": set(),
}


# ── DB 연결 ───────────────────────────────────────────────────────────────────

def get_conn() -> sqlite3.Connection:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    return conn


def init_db() -> None:
    """앱 시작 시 테이블 초기화 (없으면 생성)."""
    with get_conn() as conn:
        conn.executescript(SCHEMA)
        # 기존 컬럼 마이그레이션 (이미 존재하면 무시)
        for sql in [
            "ALTER TABLE issues ADD COLUMN created_by TEXT NOT NULL DEFAULT ''",
            "ALTER TABLE questions ADD COLUMN created_by TEXT NOT NULL DEFAULT ''",
        ]:
            try:
                conn.execute(sql)
            except sqlite3.OperationalError:
                pass
        # 기존 'leader' role → 'group_leader' 로 변환
        conn.execute("UPDATE users SET role='group_leader' WHERE role='leader'")


# ── 행 변환 헬퍼 ─────────────────────────────────────────────────────────────

def _row_to_dict(row: sqlite3.Row, table: str) -> dict:
    d = dict(row)
    for col in JSON_COLS.get(table, set()):
        if col in d and isinstance(d[col], str):
            try:
                d[col] = json.loads(d[col])
            except (json.JSONDecodeError, TypeError):
                d[col] = []
    return d


def _dict_to_values(table: str, item: dict) -> dict:
    result = dict(item)
    for col in JSON_COLS.get(table, set()):
        if col in result and not isinstance(result[col], str):
            result[col] = json.dumps(result[col], ensure_ascii=False)
    return result


# ── filename → 테이블 매핑 ───────────────────────────────────────────────────

def _resolve(filename: str):
    """
    Returns (table, collection_key) or special marker.
    collection_key: 최상위 dict 키 (예: "objectives")
    """
    MAP = {
        "okrs.json":             ("objectives",      "objectives"),
        "tasks.json":            ("tasks",           "tasks"),
        "progress.json":         ("progress_items",  "progress_items"),
        "staff.json":            ("staff",           "staff"),
        "issues.json":           ("issues",          "issues"),
        "feedback.json":         ("feedbacks",       "feedbacks"),
        "confluence_links.json": ("confluence_links","links"),
    }
    return MAP.get(filename)


# ── 알림·사용자 헬퍼 ──────────────────────────────────────────────────────────

def insert_notification(recipient: str, ntype: str, title: str, message: str, link: str) -> None:
    """알림 1건 삽입. recipient가 비어있으면 무시."""
    if not recipient:
        return
    nid = f"N{uuid.uuid4().hex[:8].upper()}"
    with get_conn() as conn:
        conn.execute(
            "INSERT INTO notifications (id,recipient,type,title,message,link,is_read,created_at) VALUES (?,?,?,?,?,?,0,?)",
            (nid, recipient, ntype, title, message, link, datetime.now().isoformat()),
        )


def get_username_by_name(name: str) -> str:
    """표시 이름으로 username 조회. 없으면 빈 문자열 반환."""
    if not name:
        return ""
    with get_conn() as conn:
        row = conn.execute("SELECT username FROM users WHERE name=?", (name,)).fetchone()
    return row["username"] if row else ""


def get_all_usernames() -> list:
    """모든 사용자 username 반환."""
    with get_conn() as conn:
        rows = conn.execute("SELECT username FROM users").fetchall()
    return [r["username"] for r in rows]


# ── load ─────────────────────────────────────────────────────────────────────

def load(filename: str) -> Any:
    init_db()
    conn = get_conn()
    try:
        # ── 일반 테이블 ──
        resolved = _resolve(filename)
        if resolved:
            table, key = resolved
            rows = conn.execute(f"SELECT * FROM {table}").fetchall()
            return {key: [_row_to_dict(r, table) for r in rows]}

        # ── qna.json: questions + answers ──
        if filename == "qna.json":
            qs = conn.execute("SELECT * FROM questions").fetchall()
            ans = conn.execute("SELECT * FROM answers").fetchall()
            return {
                "questions": [_row_to_dict(r, "questions") for r in qs],
                "answers":   [_row_to_dict(r, "answers")   for r in ans],
            }

        # ── settings.json: key-value ──
        if filename == "settings.json":
            rows = conn.execute("SELECT key, value FROM settings").fetchall()
            result = {}
            for row in rows:
                try:
                    result[row["key"]] = json.loads(row["value"])
                except (json.JSONDecodeError, TypeError):
                    result[row["key"]] = row["value"]
            return result

        # ── id_counters.json: prefix → int ──
        if filename == "id_counters.json":
            rows = conn.execute("SELECT prefix, value FROM id_counters").fetchall()
            return {row["prefix"]: row["value"] for row in rows}

        return {}
    finally:
        conn.close()


# ── save ─────────────────────────────────────────────────────────────────────

def save(filename: str, data: Any) -> None:
    init_db()
    conn = get_conn()
    try:
        with conn:
            # ── 일반 테이블 ──
            resolved = _resolve(filename)
            if resolved:
                table, key = resolved
                items = data.get(key, [])
                conn.execute(f"DELETE FROM {table}")
                for item in items:
                    vals = _dict_to_values(table, item)
                    cols = ", ".join(vals.keys())
                    placeholders = ", ".join(["?"] * len(vals))
                    conn.execute(
                        f"INSERT OR REPLACE INTO {table} ({cols}) VALUES ({placeholders})",
                        list(vals.values())
                    )
                return

            # ── qna.json ──
            if filename == "qna.json":
                conn.execute("DELETE FROM questions")
                conn.execute("DELETE FROM answers")
                for q in data.get("questions", []):
                    vals = _dict_to_values("questions", q)
                    cols = ", ".join(vals.keys())
                    ph = ", ".join(["?"] * len(vals))
                    conn.execute(f"INSERT OR REPLACE INTO questions ({cols}) VALUES ({ph})",
                                 list(vals.values()))
                for a in data.get("answers", []):
                    vals = _dict_to_values("answers", a)
                    cols = ", ".join(vals.keys())
                    ph = ", ".join(["?"] * len(vals))
                    conn.execute(f"INSERT OR REPLACE INTO answers ({cols}) VALUES ({ph})",
                                 list(vals.values()))
                return

            # ── settings.json ──
            if filename == "settings.json":
                conn.execute("DELETE FROM settings")
                for k, v in data.items():
                    encoded = json.dumps(v, ensure_ascii=False) if not isinstance(v, str) else v
                    conn.execute(
                        "INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)",
                        [k, encoded]
                    )
                return

            # ── id_counters.json ──
            if filename == "id_counters.json":
                for prefix, value in data.items():
                    conn.execute(
                        "INSERT OR REPLACE INTO id_counters (prefix, value) VALUES (?, ?)",
                        [prefix, int(value)]
                    )
                return
    finally:
        conn.close()
