from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from fastapi.responses import StreamingResponse
import csv
import io
from datetime import date
import data_store
from utils.id_generator import short_uuid
from dependencies import require_admin

router = APIRouter()


# ── 공통 CSV 응답 헬퍼 ──────────────────────────────────────────────────────────

def _csv_response(filename: str, headers: list, rows: list) -> StreamingResponse:
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(headers)
    writer.writerows(rows)
    output.seek(0)
    csv_content = '﻿' + output.getvalue()
    return StreamingResponse(
        iter([csv_content]),
        media_type="text/csv; charset=utf-8",
        headers={
            "Content-Disposition": f"attachment; filename={filename}",
            "Content-Type": "text/csv; charset=utf-8",
        },
    )


def _parse_csv(content: bytes) -> list[dict]:
    text = content.decode("utf-8-sig")
    reader = csv.DictReader(io.StringIO(text))
    return [row for row in reader]


# ── CSV export ────────────────────────────────────────────────────────────────

@router.get("/export/objectives")
def export_objectives():
    objectives = data_store.load("okrs.json").get("objectives", [])
    headers = ["objective_id", "objective_name", "tech_stack", "status", "kr_id", "kr_name"]
    rows = []
    for o in objectives:
        key_results = o.get("key_results", [])
        if key_results:
            for kr in key_results:
                rows.append([o.get("id"), o.get("name"), o.get("tech_stack"), o.get("status"), kr.get("id"), kr.get("name")])
        else:
            rows.append([o.get("id"), o.get("name"), o.get("tech_stack"), o.get("status"), "", ""])
    return _csv_response("objectives.csv", headers, rows)


@router.get("/export/tasks")
def export_tasks():
    tasks = data_store.load("tasks.json").get("tasks", [])
    headers = ["task_id", "task_name", "objective_id", "members"]
    rows = [
        [t.get("id"), t.get("name"), t.get("objective_id"),
         "; ".join(f"{m.get('name')}({m.get('username', m.get('staff_id', ''))})" for m in t.get("members", []))]
        for t in tasks
    ]
    return _csv_response("tasks.csv", headers, rows)


@router.get("/export/staff")
def export_staff():
    with data_store.get_conn() as conn:
        rows_db = conn.execute(
            "SELECT username, name, job_title, main_skills, sub_skills, learning, desired_field, okrs FROM users WHERE role='member' ORDER BY name"
        ).fetchall()
    fields = ["username", "name", "job_title", "main_skills", "sub_skills", "learning", "desired_field", "okrs"]
    rows = [[dict(r).get(f, "") for f in fields] for r in rows_db]
    return _csv_response("staff.csv", fields, rows)


@router.get("/export/progress")
def export_progress():
    items = data_store.load("progress.json").get("progress_items", [])
    fields = [
        "id", "week", "objective", "task_id", "task_name", "subtask", "planned",
        "result", "progress_percent", "issue", "assignee", "solution", "created_at", "updated_at",
    ]
    rows = [[p.get(f) for f in fields] for p in items]
    return _csv_response("progress.csv", fields, rows)


# ── CSV import ────────────────────────────────────────────────────────────────

@router.post("/import/objectives")
async def import_objectives(file: UploadFile = File(...)):
    rows = _parse_csv(await file.read())
    objectives_map: dict = {}
    for r in rows:
        obj_id = r.get("objective_id", "").strip()
        if not obj_id:
            continue
        if obj_id not in objectives_map:
            objectives_map[obj_id] = {
                "id": obj_id,
                "name": r.get("objective_name", "").strip(),
                "tech_stack": r.get("tech_stack", "").strip(),
                "key_results": [],
                "status": r.get("status", "진행중").strip(),
            }
        kr_id = r.get("kr_id", "").strip()
        if kr_id:
            objectives_map[obj_id]["key_results"].append({
                "id": kr_id,
                "name": r.get("kr_name", "").strip(),
            })
    objectives = list(objectives_map.values())
    data_store.save("okrs.json", {"objectives": objectives})
    return {"imported": len(objectives)}


@router.post("/import/tasks")
async def import_tasks(file: UploadFile = File(...)):
    rows = _parse_csv(await file.read())
    tasks = []
    for r in rows:
        members = []
        for m in r.get("members", "").strip().split(";"):
            if "(" in m and ")" in m:
                name = m.split("(")[0].strip()
                username = m.split("(")[1].replace(")", "").strip()
                members.append({"username": username, "name": name})
        tasks.append({
            "id": r.get("task_id") or short_uuid("T"),
            "name": r.get("task_name", "").strip(),
            "objective_id": r.get("objective_id", "").strip(),
            "members": members,
        })
    data_store.save("tasks.json", {"tasks": tasks})
    return {"imported": len(tasks)}


@router.post("/import/staff")
async def import_staff(file: UploadFile = File(...)):
    rows = _parse_csv(await file.read())
    fields = ["name", "role", "main_skills", "sub_skills", "learning", "desired_field", "objectives"]
    staff = [
        {"id": r.get("id") or short_uuid("S"), **{f: r.get(f, "").strip() for f in fields}}
        for r in rows
    ]
    data_store.save("staff.json", {"staff": staff})
    return {"imported": len(staff)}


@router.post("/import/progress")
async def import_progress(file: UploadFile = File(...)):
    rows = _parse_csv(await file.read())
    today = date.today().isoformat()
    str_fields = ["week", "objective", "task_id", "task_name", "subtask", "planned", "result", "issue", "assignee", "solution"]
    items = []
    for r in rows:
        item = {"id": r.get("id") or short_uuid("P"), **{f: r.get(f, "").strip() for f in str_fields}}
        item["progress_percent"] = int(r.get("progress_percent", 0) or 0)
        item["created_at"] = r.get("created_at") or today
        item["updated_at"] = r.get("updated_at") or today
        items.append(item)
    data_store.save("progress.json", {"progress_items": items})
    return {"imported": len(items)}


# ── Reset ─────────────────────────────────────────────────────────────────────

@router.delete("/reset/{target}")
def reset_data(target: str):
    allowed = {"objectives", "tasks", "staff", "progress", "all"}
    if target not in allowed:
        raise HTTPException(status_code=400, detail=f"target must be one of {allowed}")
    if target in ("objectives", "all"):
        data_store.save("okrs.json", {"objectives": []})
        counters = data_store.load("id_counters.json")
        counters.pop("O", None)
        data_store.save("id_counters.json", counters)
    if target in ("tasks", "all"):
        data_store.save("tasks.json", {"tasks": []})
        counters = data_store.load("id_counters.json")
        counters.pop("T", None)
        data_store.save("id_counters.json", counters)
    if target in ("staff", "all"):
        data_store.save("staff.json", {"staff": []})
    if target in ("progress", "all"):
        data_store.save("progress.json", {"progress_items": []})
    return {"reset": target}
