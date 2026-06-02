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


class SubTaskUpdate(BaseModel):
    name: Optional[str] = None
    done: Optional[bool] = None
    members: Optional[List[TaskMember]] = None


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


class AbsorbBody(BaseModel):
    parent_id: str


class PromoteBody(BaseModel):
    parent_id: str  # 어느 부모에서 분리할지


def _collect_member_usernames(task: dict) -> set:
    """대과제(+소과제) 전체 멤버 username 수집."""
    usernames = {m["username"] for m in task.get("members", []) if m.get("username")}
    for st in task.get("sub_tasks", []):
        usernames |= {m["username"] for m in st.get("members", []) if m.get("username")}
    return usernames


def _sync_task_ids_absorb(absorbed_id: str, sub_ids: set, parent_id: str):
    """absorb 시: absorbed_id / sub_ids 보유 유저에게 parent_id 추가."""
    trigger_ids = {absorbed_id} | sub_ids
    with data_store.get_conn() as conn:
        for row in conn.execute("SELECT username, task_ids FROM users").fetchall():
            try:
                ids = json.loads(row["task_ids"] or "[]")
            except (json.JSONDecodeError, TypeError):
                ids = []
            if any(tid in ids for tid in trigger_ids) and parent_id not in ids:
                ids.append(parent_id)
                conn.execute(
                    "UPDATE users SET task_ids=? WHERE username=?",
                    (json.dumps(ids, ensure_ascii=False), row["username"]),
                )


def _sync_task_ids_promote(sub_task_id: str, parent_id: str, remaining_sub_ids: set):
    """promote 시: 해당 부모의 다른 소과제가 없는 유저에게서 parent_id 제거."""
    with data_store.get_conn() as conn:
        for row in conn.execute("SELECT username, task_ids FROM users").fetchall():
            try:
                ids = json.loads(row["task_ids"] or "[]")
            except (json.JSONDecodeError, TypeError):
                ids = []
            if parent_id not in ids:
                continue
            still_needs_parent = any(sid in ids for sid in remaining_sub_ids)
            if not still_needs_parent and parent_id in ids:
                ids.remove(parent_id)
                conn.execute(
                    "UPDATE users SET task_ids=? WHERE username=?",
                    (json.dumps(ids, ensure_ascii=False), row["username"]),
                )


@router.post("/{task_id}/absorb")
def absorb_task(task_id: str, body: AbsorbBody):
    """대과제 task_id를 대과제 body.parent_id의 소과제로 편입."""
    if task_id == body.parent_id:
        raise HTTPException(status_code=400, detail="자기 자신에게 편입할 수 없습니다")

    tasks = _load()

    task   = next((t for t in tasks if t["id"] == task_id), None)
    parent = next((t for t in tasks if t["id"] == body.parent_id), None)

    if not task:
        raise HTTPException(status_code=404, detail="편입할 과제를 찾을 수 없습니다")
    if not parent:
        raise HTTPException(status_code=404, detail="대상 모과제를 찾을 수 없습니다")

    # 순환 참조 방지: parent_id가 이미 task의 소과제인지 확인
    task_sub_ids = {st["id"] for st in task.get("sub_tasks", [])}
    if body.parent_id in task_sub_ids:
        raise HTTPException(status_code=400, detail="순환 참조: 대상 과제가 이미 소과제입니다")

    old_obj = task.get("objective_id", "")
    new_obj = parent.get("objective_id", "")

    # task 자체 → 소과제로 변환 (members 포함)
    new_sub = {
        "id":      task["id"],
        "name":    task["name"],
        "done":    False,
        "members": task.get("members", []),
    }

    # parent의 sub_tasks에 task + task의 기존 소과제 일괄 추가 (flatten)
    parent_subs = list(parent.get("sub_tasks", []))
    parent_subs.append(new_sub)
    parent_subs.extend(task.get("sub_tasks", []))

    # tasks 저장: task 제거, parent 업데이트
    new_tasks = [t for t in tasks if t["id"] != task_id]
    for i, t in enumerate(new_tasks):
        if t["id"] == body.parent_id:
            new_tasks[i] = {**t, "sub_tasks": parent_subs}
            break
    _save(new_tasks)

    # users.task_ids 동기화
    _sync_task_ids_absorb(task_id, task_sub_ids, body.parent_id)

    # OKR 동기화
    member_usernames = _collect_member_usernames(task)
    if member_usernames and old_obj != new_obj:
        _sync_staff_okrs(member_usernames, old_obj, new_obj, new_tasks)

    return next(t for t in new_tasks if t["id"] == body.parent_id)


@router.post("/{task_id}/promote")
def promote_sub_task(task_id: str, body: PromoteBody):
    """소과제 task_id를 독립 대과제로 분리."""
    tasks = _load()

    parent = next((t for t in tasks if t["id"] == body.parent_id), None)
    if not parent:
        raise HTTPException(status_code=404, detail="모과제를 찾을 수 없습니다")

    st = next((s for s in parent.get("sub_tasks", []) if s["id"] == task_id), None)
    if not st:
        raise HTTPException(status_code=404, detail="해당 소과제를 찾을 수 없습니다")

    old_obj = parent.get("objective_id", "")

    # 새 독립 과제 생성 (objective 없음, target은 모과제 상속)
    new_task = {
        "id":           task_id,
        "name":         st["name"],
        "objective_id": "",
        "target":       parent.get("target", ""),
        "members":      st.get("members", []),
        "sub_tasks":    [],
    }

    # parent에서 소과제 제거
    remaining_subs = [s for s in parent.get("sub_tasks", []) if s["id"] != task_id]
    remaining_sub_ids = {s["id"] for s in remaining_subs}

    new_tasks = []
    for t in tasks:
        if t["id"] == body.parent_id:
            new_tasks.append({**t, "sub_tasks": remaining_subs})
        else:
            new_tasks.append(t)
    new_tasks.append(new_task)
    _save(new_tasks)

    # users.task_ids 동기화: 이 소과제의 다른 형제가 없는 유저는 parent_id 제거
    _sync_task_ids_promote(task_id, body.parent_id, remaining_sub_ids)

    # OKR 동기화: 분리된 과제는 objective 없음 → old_obj 제거
    member_usernames = {m["username"] for m in st.get("members", []) if m.get("username")}
    if member_usernames and old_obj:
        _sync_staff_okrs(member_usernames, old_obj, "", new_tasks)

    return new_task


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
