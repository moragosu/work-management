import json
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import data_store
from utils.id_generator import next_counter_id, get_reusable_ids, get_next_id_preview, sync_counter

router = APIRouter()


class TaskMember(BaseModel):
    username: str
    name: str
    role: str = ""


class SubTask(BaseModel):
    id: str
    name: str
    done: bool = False
    members: List[TaskMember] = []
    target: str = ""


class SubTaskUpdate(BaseModel):
    name: Optional[str] = None
    done: Optional[bool] = None
    members: Optional[List[TaskMember]] = None
    target: Optional[str] = None


class Task(BaseModel):
    id: str
    name: str
    objective_id: str = ""
    target: str = ""
    members: List[TaskMember] = []
    sub_tasks: List[SubTask] = []


class TaskUpdate(BaseModel):
    name: Optional[str] = None
    objective_id: Optional[str] = None
    target: Optional[str] = None
    members: Optional[List[TaskMember]] = None
    sub_tasks: Optional[List[SubTask]] = None


def _load() -> list:
    data = data_store.load("tasks.json")
    return data.get("tasks", [])


def _save(tasks: list) -> None:
    data_store.save("tasks.json", {"tasks": tasks})


def _cascade_delete_ids(ids_to_remove: set, task_name: str = "") -> None:
    """users.task_ids, progress, questions, issues에서 해당 ID들 제거."""
    placeholders = ",".join("?" * len(ids_to_remove))
    id_list = list(ids_to_remove)

    with data_store.get_conn() as conn:
        # users.task_ids 갱신
        rows = conn.execute(
            "SELECT username, task_ids FROM users WHERE role='member'"
        ).fetchall()
        for row in rows:
            try:
                ids = json.loads(row["task_ids"] or "[]")
            except (json.JSONDecodeError, TypeError):
                ids = []
            new_ids = [x for x in ids if x not in ids_to_remove]
            if len(new_ids) != len(ids):
                conn.execute(
                    "UPDATE users SET task_ids=? WHERE username=?",
                    (json.dumps(new_ids, ensure_ascii=False), row["username"])
                )

        # 질문·답변·대댓글 삭제
        q_ids = [r["id"] for r in conn.execute(
            f"SELECT id FROM questions WHERE task_id IN ({placeholders})", id_list
        ).fetchall()]
        if q_ids:
            q_ph = ",".join("?" * len(q_ids))
            a_ids = [r["id"] for r in conn.execute(
                f"SELECT id FROM answers WHERE question_id IN ({q_ph})", q_ids
            ).fetchall()]
            if a_ids:
                a_ph = ",".join("?" * len(a_ids))
                conn.execute(f"DELETE FROM answer_replies WHERE answer_id IN ({a_ph})", a_ids)
            conn.execute(f"DELETE FROM answers WHERE question_id IN ({q_ph})", q_ids)
            conn.execute(f"DELETE FROM questions WHERE id IN ({q_ph})", q_ids)

        # 이슈·댓글 삭제
        i_ids = [r["id"] for r in conn.execute(
            f"SELECT id FROM issues WHERE task_id IN ({placeholders})", id_list
        ).fetchall()]
        if i_ids:
            i_ph = ",".join("?" * len(i_ids))
            conn.execute(f"DELETE FROM issue_comments WHERE issue_id IN ({i_ph})", i_ids)
            conn.execute(f"DELETE FROM issues WHERE id IN ({i_ph})", i_ids)

        # confluence_links 삭제
        conn.execute(f"DELETE FROM confluence_links WHERE task_id IN ({placeholders})", id_list)

    progress_data = data_store.load("progress.json")
    changed = False
    for item in progress_data.get("progress_items", []):
        if item.get("task_id") in ids_to_remove:
            item["task_id"] = ""
            item["task_name"] = task_name
            changed = True
    if changed:
        data_store.save("progress.json", progress_data)


# ── Task endpoints ─────────────────────────────────────────────────────────────

@router.get("", response_model=List[Task])
def list_tasks(objective_id: Optional[str] = None):
    tasks = _load()
    if objective_id:
        tasks = [t for t in tasks if t.get("objective_id") == objective_id]
    return tasks


@router.get("/next-id")
def get_next_id():
    tasks = _load()
    return {"next_id": get_next_id_preview("T", tasks)}


@router.get("/reusable-ids")
def get_reusable_task_ids():
    tasks = _load()
    return {"reusable_ids": get_reusable_ids(tasks, "T")}


@router.get("/{task_id}/history")
def get_task_history(task_id: str):
    tasks = _load()
    task = next((t for t in tasks if t["id"] == task_id), None)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    sub_task_ids = [st["id"] for st in task.get("sub_tasks", [])]
    all_ids = [task_id] + sub_task_ids

    # 이슈 조회
    all_issues = data_store.load("issues.json").get("issues", [])
    issues = [i for i in all_issues if i.get("task_id") in all_ids]

    if issues:
        issue_ids = [i["id"] for i in issues]
        placeholders = ",".join("?" * len(issue_ids))
        with data_store.get_conn() as conn:
            all_comments = [dict(r) for r in conn.execute(
                f"SELECT * FROM issue_comments WHERE issue_id IN ({placeholders}) ORDER BY created_at",
                issue_ids,
            ).fetchall()]
    else:
        all_comments = []

    for iss in issues:
        top = [c for c in all_comments if c["issue_id"] == iss["id"] and not c["parent_id"]]
        for c in top:
            c["replies"] = [r for r in all_comments if r["parent_id"] == c["id"]]
        iss["comments"] = top

    # Q&A 조회
    qna_data = data_store.load("qna.json")
    all_questions = qna_data.get("questions", [])
    all_answers = qna_data.get("answers", [])
    questions = [q for q in all_questions if q.get("task_id") in all_ids]

    with data_store.get_conn() as conn:
        all_replies = [dict(r) for r in conn.execute(
            "SELECT * FROM answer_replies ORDER BY created_at"
        ).fetchall()]

    q_ids = {q["id"] for q in questions}
    for q in questions:
        q_answers = []
        for a in all_answers:
            if a["question_id"] == q["id"]:
                a_dict = dict(a)
                a_dict["replies"] = [r for r in all_replies if r["answer_id"] == a["id"]]
                q_answers.append(a_dict)
        q["answers"] = q_answers

    # 컨플루언스 링크 조회
    all_links = data_store.load("confluence_links.json").get("links", [])
    links = [l for l in all_links if l.get("task_id") in all_ids]

    # 주차별 그룹핑
    week_map: dict = {}
    for iss in issues:
        w = iss.get("week", "")
        week_map.setdefault(w, {"week": w, "issues": [], "questions": [], "confluence_links": []})
        week_map[w]["issues"].append(iss)
    for q in questions:
        w = q.get("week", "")
        week_map.setdefault(w, {"week": w, "issues": [], "questions": [], "confluence_links": []})
        week_map[w]["questions"].append(q)
    for lnk in links:
        w = lnk.get("week", "")
        week_map.setdefault(w, {"week": w, "issues": [], "questions": [], "confluence_links": []})
        week_map[w]["confluence_links"].append(lnk)

    weeks = sorted(week_map.values(), key=lambda x: x["week"], reverse=True)
    return {"task": task, "weeks": weeks}


@router.get("/{task_id}", response_model=Task)
def get_task(task_id: str):
    tasks = _load()
    for t in tasks:
        if t["id"] == task_id:
            return t
    raise HTTPException(status_code=404, detail="Task not found")


@router.post("", response_model=Task, status_code=201)
def create_task(task: Task):
    tasks = _load()
    if not task.id:
        task.id = next_counter_id("T", tasks)
    else:
        sync_counter("T", task.id, tasks)
    if any(t["id"] == task.id for t in tasks):
        raise HTTPException(status_code=400, detail="Task id already exists")
    tasks.append(task.model_dump())
    _save(tasks)
    return task


class BulkTargetUpdate(BaseModel):
    task_ids: List[str]
    target: str


@router.put("/bulk-target")
def bulk_update_target(update: BulkTargetUpdate):
    tasks = _load()
    id_set = set(update.task_ids)
    count = 0
    for i, t in enumerate(tasks):
        if t["id"] in id_set:
            tasks[i] = {**t, "target": update.target}
            count += 1
    _save(tasks)
    return {"updated": count}


@router.put("/{task_id}/sub-tasks/{sub_task_id}")
def update_sub_task(task_id: str, sub_task_id: str, update: SubTaskUpdate):
    tasks = _load()
    for i, t in enumerate(tasks):
        if t["id"] == task_id:
            sub_tasks = t.get("sub_tasks", [])
            for j, st in enumerate(sub_tasks):
                if st["id"] == sub_task_id:
                    patch = update.model_dump(exclude_none=True)
                    sub_tasks[j] = {**st, **patch}
                    tasks[i]["sub_tasks"] = sub_tasks
                    _save(tasks)
                    return sub_tasks[j]
            raise HTTPException(status_code=404, detail="Sub-task not found")
    raise HTTPException(status_code=404, detail="Task not found")


@router.delete("/{task_id}/sub-tasks/{sub_task_id}")
def delete_sub_task(task_id: str, sub_task_id: str):
    tasks = _load()
    for i, t in enumerate(tasks):
        if t["id"] == task_id:
            sub_tasks = t.get("sub_tasks", [])
            st = next((s for s in sub_tasks if s["id"] == sub_task_id), None)
            if not st:
                raise HTTPException(status_code=404, detail="Sub-task not found")
            tasks[i]["sub_tasks"] = [s for s in sub_tasks if s["id"] != sub_task_id]
            _save(tasks)
            _cascade_delete_ids({sub_task_id}, t["name"])
            return {"deleted": sub_task_id}
    raise HTTPException(status_code=404, detail="Task not found")


@router.put("/{task_id}", response_model=Task)
def update_task(task_id: str, update: TaskUpdate):
    tasks = _load()
    for i, t in enumerate(tasks):
        if t["id"] == task_id:
            old_objective_id = t.get("objective_id", "")
            new_objective_id = update.objective_id if update.objective_id is not None else old_objective_id
            patch = update.model_dump(exclude_none=True)
            tasks[i] = {**t, **patch}
            _save(tasks)
            if old_objective_id != new_objective_id:
                member_usernames = {m["username"] for m in t.get("members", []) if m.get("username")}
                if member_usernames:
                    _sync_staff_okrs(member_usernames, old_objective_id, new_objective_id, tasks)
            return tasks[i]
    raise HTTPException(status_code=404, detail="Task not found")


def _sync_staff_okrs(member_usernames: set, old_obj_id: str, new_obj_id: str, all_tasks: list):
    """task objective_id 변경 시 관련 users.okrs 자동 동기화."""
    with data_store.get_conn() as conn:
        for username in member_usernames:
            row = conn.execute(
                "SELECT okrs FROM users WHERE username=?", (username,)
            ).fetchone()
            if not row:
                continue
            okrs = [x.strip() for x in (row["okrs"] or "").split(",") if x.strip()]
            if old_obj_id:
                still_connected = any(
                    t.get("objective_id") == old_obj_id and (
                        any(m.get("username") == username for m in t.get("members", [])) or
                        any(
                            any(m.get("username") == username for m in st.get("members", []))
                            for st in t.get("sub_tasks", [])
                        )
                    )
                    for t in all_tasks
                )
                if not still_connected and old_obj_id in okrs:
                    okrs.remove(old_obj_id)
            if new_obj_id and new_obj_id not in okrs:
                okrs.append(new_obj_id)
            conn.execute(
                "UPDATE users SET okrs=? WHERE username=?",
                (",".join(okrs), username)
            )


import re as _re

# ── 편입·분리 공통 헬퍼 ─────────────────────────────────────────────────────────

def _rename_task_id(old_id: str, new_id: str) -> None:
    """DB 내 모든 task_id 참조를 old_id → new_id로 단일 트랜잭션에서 업데이트."""
    if old_id == new_id:
        return
    with data_store.get_conn() as conn:
        conn.execute("UPDATE issues            SET task_id=? WHERE task_id=?", (new_id, old_id))
        conn.execute("UPDATE questions         SET task_id=? WHERE task_id=?", (new_id, old_id))
        conn.execute("UPDATE confluence_links  SET task_id=? WHERE task_id=?", (new_id, old_id))
        # users.task_ids (JSON 배열)
        for row in conn.execute("SELECT username, task_ids FROM users").fetchall():
            try:
                ids = json.loads(row["task_ids"] or "[]")
            except (json.JSONDecodeError, TypeError):
                ids = []
            if old_id in ids:
                ids[ids.index(old_id)] = new_id
                conn.execute(
                    "UPDATE users SET task_ids=? WHERE username=?",
                    (json.dumps(ids, ensure_ascii=False), row["username"]),
                )
        # staff.selected_tasks (콤마 문자열)
        for row in conn.execute("SELECT id, selected_tasks FROM staff WHERE selected_tasks != ''").fetchall():
            parts = [s.strip() for s in row["selected_tasks"].split(",")]
            if old_id in parts:
                parts[parts.index(old_id)] = new_id
                conn.execute(
                    "UPDATE staff SET selected_tasks=? WHERE id=?",
                    (", ".join(parts), row["id"]),
                )
    # progress_items: JSON 파일 기반 (트랜잭션 외부, 마지막 처리)
    progress = data_store.load("progress.json")
    changed = False
    for item in progress.get("progress_items", []):
        if item.get("task_id") == old_id:
            item["task_id"] = new_id
            changed = True
    if changed:
        data_store.save("progress.json", progress)


def _next_sub_task_id(parent_id: str, parent_subs: list) -> str:
    """모과제 소과제 목록에서 다음 순번 ID 반환."""
    prefix = f"{parent_id}-"
    nums = [int(s["id"][len(prefix):]) for s in parent_subs
            if s["id"].startswith(prefix) and s["id"][len(prefix):].isdigit()]
    return f"{parent_id}-{max(nums, default=0) + 1}"


def _reusable_sub_task_ids(parent_id: str, parent_subs: list) -> list:
    """모과제 소과제 목록에서 빈 번호(재사용 가능) 목록 반환."""
    prefix = f"{parent_id}-"
    nums = {int(s["id"][len(prefix):]) for s in parent_subs
            if s["id"].startswith(prefix) and s["id"][len(prefix):].isdigit()}
    max_n = max(nums, default=0)
    return [f"{parent_id}-{n}" for n in range(1, max_n + 1) if n not in nums]


def _collect_member_usernames(task: dict) -> set:
    """대과제(+소과제) 전체 멤버 username 수집."""
    usernames = {m["username"] for m in task.get("members", []) if m.get("username")}
    for st in task.get("sub_tasks", []):
        usernames |= {m["username"] for m in st.get("members", []) if m.get("username")}
    return usernames


def _add_parent_to_task_ids(new_sub_id: str, parent_id: str) -> None:
    """new_sub_id 보유 유저에게 parent_id 추가."""
    with data_store.get_conn() as conn:
        for row in conn.execute("SELECT username, task_ids FROM users").fetchall():
            try:
                ids = json.loads(row["task_ids"] or "[]")
            except (json.JSONDecodeError, TypeError):
                ids = []
            if new_sub_id in ids and parent_id not in ids:
                ids.append(parent_id)
                conn.execute(
                    "UPDATE users SET task_ids=? WHERE username=?",
                    (json.dumps(ids, ensure_ascii=False), row["username"]),
                )


def _remove_parent_from_task_ids(new_task_id: str, parent_id: str,
                                  remaining_sub_ids: set, parent_direct_usernames: set) -> None:
    """분리 후: 다른 형제 소과제도 없고 직접 담당자도 아닌 유저에서 parent_id 제거."""
    with data_store.get_conn() as conn:
        for row in conn.execute("SELECT username, task_ids FROM users").fetchall():
            try:
                ids = json.loads(row["task_ids"] or "[]")
            except (json.JSONDecodeError, TypeError):
                ids = []
            if parent_id not in ids:
                continue
            still_needs = (
                any(sid in ids for sid in remaining_sub_ids)
                or row["username"] in parent_direct_usernames
            )
            if not still_needs:
                ids.remove(parent_id)
                conn.execute(
                    "UPDATE users SET task_ids=? WHERE username=?",
                    (json.dumps(ids, ensure_ascii=False), row["username"]),
                )


# ── 편입·분리 Model ────────────────────────────────────────────────────────────

class AbsorbBody(BaseModel):
    parent_id: str
    new_sub_id: str   # 프론트에서 선택한 새 소과제 ID (예: T5-3)


class PromoteBody(BaseModel):
    parent_id: str
    new_task_id: str  # 프론트에서 선택한 새 대과제 ID (예: T23)


# ── 편입·분리 보조 엔드포인트 ──────────────────────────────────────────────────

@router.get("/{parent_id}/reusable-sub-ids")
def get_reusable_sub_ids(parent_id: str):
    """편입 모달용: 모과제의 다음 소과제 ID와 재사용 가능 빈 번호 반환."""
    tasks = _load()
    parent = next((t for t in tasks if t["id"] == parent_id), None)
    if not parent:
        raise HTTPException(status_code=404, detail="Task not found")
    subs = parent.get("sub_tasks", [])
    return {
        "next":     _next_sub_task_id(parent_id, subs),
        "reusable": _reusable_sub_task_ids(parent_id, subs),
    }


# ── 편입 (absorb) ─────────────────────────────────────────────────────────────

@router.post("/{task_id}/absorb")
def absorb_task(task_id: str, body: AbsorbBody):
    """대과제 task_id를 대과제 body.parent_id의 소과제로 편입. 새 소과제 ID 부여."""
    # ── 기본 검증 ──
    if task_id == body.parent_id:
        raise HTTPException(400, "자기 자신에게 편입할 수 없습니다")

    # new_sub_id 형식: {parent_id}-{양수}
    expected_prefix = f"{body.parent_id}-"
    suffix = body.new_sub_id[len(expected_prefix):]
    if not body.new_sub_id.startswith(expected_prefix) or not suffix.isdigit() or int(suffix) <= 0:
        raise HTTPException(400, f"소과제 ID 형식이 올바르지 않습니다 (예: {body.parent_id}-1)")

    tasks = _load()
    task   = next((t for t in tasks if t["id"] == task_id), None)
    parent = next((t for t in tasks if t["id"] == body.parent_id), None)

    if not task:
        raise HTTPException(404, "편입할 과제를 찾을 수 없습니다")
    if not parent:
        raise HTTPException(404, "대상 모과제를 찾을 수 없습니다")

    # 소과제 보유 과제 편입 불가
    if task.get("sub_tasks"):
        raise HTTPException(400, "소과제가 있는 과제는 편입할 수 없습니다. 소과제를 먼저 정리하세요.")

    # new_sub_id 중복 체크
    all_sub_ids = {st["id"] for t in tasks for st in t.get("sub_tasks", [])}
    if body.new_sub_id in all_sub_ids:
        raise HTTPException(400, "이미 사용 중인 소과제 ID입니다")

    old_obj = task.get("objective_id", "")
    new_obj = parent.get("objective_id", "")

    # 새 소과제 엔트리 (새 ID 사용, 원래 target 유지)
    new_sub = {
        "id":      body.new_sub_id,
        "name":    task["name"],
        "done":    False,
        "members": task.get("members", []),
        "target":  task.get("target", ""),
    }

    # parent sub_tasks에 추가
    parent_subs = list(parent.get("sub_tasks", [])) + [new_sub]
    # 소과제 ID 순 정렬 (접미 숫자 기준)
    parent_subs.sort(key=lambda s: int(s["id"].split("-")[-1]) if s["id"].split("-")[-1].isdigit() else 0)

    # ① tasks 저장 (task 제거, parent 업데이트)
    new_tasks = [t for t in tasks if t["id"] != task_id]
    for i, t in enumerate(new_tasks):
        if t["id"] == body.parent_id:
            new_tasks[i] = {**t, "sub_tasks": parent_subs}
            break
    _save(new_tasks)

    # ② DB 참조 업데이트: old task_id → new_sub_id (단일 트랜잭션 + progress_items)
    _rename_task_id(task_id, body.new_sub_id)

    # ③ parent_id를 new_sub_id 보유 유저의 task_ids에 추가
    _add_parent_to_task_ids(body.new_sub_id, body.parent_id)

    # ④ OKR 동기화
    member_usernames = {m["username"] for m in task.get("members", []) if m.get("username")}
    if member_usernames and old_obj != new_obj:
        _sync_staff_okrs(member_usernames, old_obj, new_obj, new_tasks)

    return next(t for t in new_tasks if t["id"] == body.parent_id)


# ── 분리 (promote) ────────────────────────────────────────────────────────────

@router.post("/{task_id}/promote")
def promote_sub_task(task_id: str, body: PromoteBody):
    """소과제 task_id를 독립 대과제로 분리. 새 대과제 ID 부여."""
    # new_task_id 형식: T{양수}
    if not _re.fullmatch(r"T\d+", body.new_task_id):
        raise HTTPException(400, "과제 ID 형식이 올바르지 않습니다 (예: T23)")

    tasks = _load()

    # new_task_id 중복 체크
    if any(t["id"] == body.new_task_id for t in tasks):
        raise HTTPException(400, "이미 사용 중인 과제 ID입니다")

    parent = next((t for t in tasks if t["id"] == body.parent_id), None)
    if not parent:
        raise HTTPException(404, "모과제를 찾을 수 없습니다")

    st = next((s for s in parent.get("sub_tasks", []) if s["id"] == task_id), None)
    if not st:
        raise HTTPException(404, "해당 소과제를 찾을 수 없습니다")

    old_obj = parent.get("objective_id", "")

    # 새 대과제 생성 (objective 없음, target 모과제 상속)
    new_task = {
        "id":           body.new_task_id,
        "name":         st["name"],
        "objective_id": "",
        "target":       parent.get("target", ""),
        "members":      st.get("members", []),
        "sub_tasks":    [],
    }

    # parent에서 소과제 제거
    remaining_subs    = [s for s in parent.get("sub_tasks", []) if s["id"] != task_id]
    remaining_sub_ids = {s["id"] for s in remaining_subs}

    # ① tasks 저장
    new_tasks = []
    for t in tasks:
        if t["id"] == body.parent_id:
            new_tasks.append({**t, "sub_tasks": remaining_subs})
        else:
            new_tasks.append(t)
    new_tasks.append(new_task)
    _save(new_tasks)

    # ② DB 참조 업데이트: old sub_task_id → new_task_id
    _rename_task_id(task_id, body.new_task_id)

    # ③ counter 동기화 (재사용 ID 선택 시 counter는 내려가지 않음)
    sync_counter("T", body.new_task_id, new_tasks)

    # ④ parent_id 제거: 형제 없고 직접 담당자도 아닌 유저에서
    parent_direct = {m["username"] for m in parent.get("members", []) if m.get("username")}
    _remove_parent_from_task_ids(body.new_task_id, body.parent_id, remaining_sub_ids, parent_direct)

    # ⑤ OKR 동기화: 분리 과제는 objective 없음 → old_obj 제거
    member_usernames = {m["username"] for m in st.get("members", []) if m.get("username")}
    if member_usernames and old_obj:
        _sync_staff_okrs(member_usernames, old_obj, "", new_tasks)

    return new_task


# ── 소과제 이동 (move) ────────────────────────────────────────────────────────

class MoveSubTaskBody(BaseModel):
    from_parent_id: str
    to_parent_id: str
    new_sub_id: str   # 대상 모과제 기준 새 소과제 ID (예: T3-2)


@router.post("/{task_id}/move-sub-task")
def move_sub_task(task_id: str, body: MoveSubTaskBody):
    """소과제 task_id를 from_parent에서 to_parent로 이동. 새 소과제 ID 부여."""
    if body.from_parent_id == body.to_parent_id:
        raise HTTPException(400, "출발 모과제와 도착 모과제가 같습니다")

    # new_sub_id 형식: {to_parent_id}-{양수}
    expected_prefix = f"{body.to_parent_id}-"
    suffix = body.new_sub_id[len(expected_prefix):]
    if not body.new_sub_id.startswith(expected_prefix) or not suffix.isdigit() or int(suffix) <= 0:
        raise HTTPException(400, f"소과제 ID 형식이 올바르지 않습니다 (예: {body.to_parent_id}-1)")

    tasks = _load()
    from_parent = next((t for t in tasks if t["id"] == body.from_parent_id), None)
    to_parent   = next((t for t in tasks if t["id"] == body.to_parent_id), None)

    if not from_parent:
        raise HTTPException(404, "출발 모과제를 찾을 수 없습니다")
    if not to_parent:
        raise HTTPException(404, "도착 모과제를 찾을 수 없습니다")

    st = next((s for s in from_parent.get("sub_tasks", []) if s["id"] == task_id), None)
    if not st:
        raise HTTPException(404, "해당 소과제를 찾을 수 없습니다")

    # new_sub_id 중복 체크
    all_sub_ids = {s["id"] for t in tasks for s in t.get("sub_tasks", [])}
    if body.new_sub_id in all_sub_ids:
        raise HTTPException(400, "이미 사용 중인 소과제 ID입니다")

    old_obj = from_parent.get("objective_id", "")
    new_obj = to_parent.get("objective_id", "")

    # 새 소과제 엔트리 (새 ID, 기존 데이터 유지)
    new_sub = {**st, "id": body.new_sub_id}

    # from_parent에서 제거, to_parent에 추가
    from_subs     = [s for s in from_parent.get("sub_tasks", []) if s["id"] != task_id]
    to_subs       = list(to_parent.get("sub_tasks", [])) + [new_sub]
    to_subs.sort(key=lambda s: int(s["id"].split("-")[-1]) if s["id"].split("-")[-1].isdigit() else 0)

    new_tasks = []
    for t in tasks:
        if t["id"] == body.from_parent_id:
            new_tasks.append({**t, "sub_tasks": from_subs})
        elif t["id"] == body.to_parent_id:
            new_tasks.append({**t, "sub_tasks": to_subs})
        else:
            new_tasks.append(t)
    _save(new_tasks)

    # ① DB 참조: old sub_id → new_sub_id
    _rename_task_id(task_id, body.new_sub_id)

    # ② to_parent_id를 new_sub_id 보유 유저에게 추가
    _add_parent_to_task_ids(body.new_sub_id, body.to_parent_id)

    # ③ from_parent_id: 형제 없고 직접 담당자 아닌 유저에서 제거
    from_remaining = {s["id"] for s in from_subs}
    from_direct    = {m["username"] for m in from_parent.get("members", []) if m.get("username")}
    _remove_parent_from_task_ids(body.new_sub_id, body.from_parent_id, from_remaining, from_direct)

    # ④ OKR 동기화
    member_usernames = {m["username"] for m in st.get("members", []) if m.get("username")}
    if member_usernames and old_obj != new_obj:
        _sync_staff_okrs(member_usernames, old_obj, new_obj, new_tasks)

    return next(t for t in new_tasks if t["id"] == body.to_parent_id)


@router.delete("/{task_id}")
def delete_task(task_id: str):
    tasks = _load()
    task = next((t for t in tasks if t["id"] == task_id), None)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    task_name = task["name"]
    sub_task_ids = {st["id"] for st in task.get("sub_tasks", [])}
    all_ids = {task_id} | sub_task_ids

    _cascade_delete_ids(all_ids, task_name)

    new_tasks = [t for t in tasks if t["id"] != task_id]
    _save(new_tasks)
    return {"deleted": task_id}


# ── Related data endpoints ────────────────────────────────────────────────────

@router.get("/{task_id}/related")
def get_task_related_data(task_id: str):
    tasks = _load()
    task = next((t for t in tasks if t["id"] == task_id), None)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    objectives_data = data_store.load("okrs.json")

    related_objective = None
    if task.get("objective_id"):
        related_objective = next(
            (o for o in objectives_data.get("objectives", []) if o["id"] == task["objective_id"]), None
        )

    usernames = [m.get("username") for m in task.get("members", []) if m.get("username")]
    related_staff = []
    if usernames:
        ph = ",".join("?" * len(usernames))
        with data_store.get_conn() as conn:
            rows = conn.execute(
                f"SELECT username, name, job_title, main_skills FROM users WHERE username IN ({ph})",
                usernames
            ).fetchall()
        related_staff = [dict(r) for r in rows]

    return {"task": task, "related_objective": related_objective, "related_staff": related_staff}
