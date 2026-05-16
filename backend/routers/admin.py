from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import StreamingResponse
import csv
import io
import uuid
from datetime import date
import data_store

router = APIRouter()


# ── CSV export ────────────────────────────────────────────────────────────────

@router.get("/export/objectives")
def export_objectives():
    """Export objectives with key results as CSV."""
    objectives = data_store.load("okrs.json").get("objectives", [])
    output = io.BytesIO()
    writer = csv.writer(io.TextIOWrapper(output, encoding='utf-8-sig', newline=''))
    writer.writerow([
        "objective_id", "objective_name", "tech_stack", "status",
        "kr_id", "kr_name"
    ])
    for o in objectives:
        key_results = o.get("key_results", [])
        if key_results:
            for kr in key_results:
                writer.writerow([
                    o.get("id"), o.get("name"),
                    o.get("tech_stack"), o.get("status"),
                    kr.get("id"), kr.get("name"),
                ])
        else:
            writer.writerow([
                o.get("id"), o.get("name"),
                o.get("tech_stack"), o.get("status"),
                "", "",
            ])
    output.seek(0)
    return StreamingResponse(
        output,
        media_type="text/csv; charset=utf-8",
        headers={
            "Content-Disposition": "attachment; filename*=UTF-8''objectives.csv",
            "Content-Type": "text/csv; charset=utf-8"
        },
    )


@router.get("/export/tasks")
def export_tasks():
    """Export tasks as CSV."""
    tasks = data_store.load("tasks.json").get("tasks", [])
    output = io.BytesIO()
    writer = csv.writer(io.TextIOWrapper(output, encoding='utf-8-sig', newline=''))
    writer.writerow(["task_id", "task_name", "objective_id", "members"])
    for t in tasks:
        members_str = "; ".join([f"{m.get('name')}({m.get('staff_id')})" for m in t.get("members", [])])
        writer.writerow([
            t.get("id"), t.get("name"), t.get("objective_id"), members_str
        ])
    output.seek(0)
    return StreamingResponse(
        output,
        media_type="text/csv; charset=utf-8",
        headers={
            "Content-Disposition": "attachment; filename*=UTF-8''tasks.csv",
            "Content-Type": "text/csv; charset=utf-8"
        },
    )


@router.get("/export/staff")
def export_staff():
    staff = data_store.load("staff.json").get("staff", [])
    output = io.BytesIO()
    writer = csv.writer(io.TextIOWrapper(output, encoding='utf-8-sig', newline=''))
    writer.writerow(["id", "name", "role", "main_skills", "sub_skills", "learning", "desired_field", "objectives"])
    for s in staff:
        writer.writerow([
            s.get("id"), s.get("name"), s.get("role"),
            s.get("main_skills"), s.get("sub_skills"),
            s.get("learning"), s.get("desired_field"), s.get("objectives"),
        ])
    output.seek(0)
    return StreamingResponse(
        output,
        media_type="text/csv; charset=utf-8",
        headers={
            "Content-Disposition": "attachment; filename*=UTF-8''staff.csv",
            "Content-Type": "text/csv; charset=utf-8"
        },
    )


@router.get("/export/progress")
def export_progress():
    items = data_store.load("progress.json").get("progress_items", [])
    output = io.BytesIO()
    writer = csv.writer(io.TextIOWrapper(output, encoding='utf-8-sig', newline=''))
    writer.writerow([
        "id", "week", "objective", "task_id", "task_name", "subtask", "planned",
        "result", "progress_percent", "issue", "assignee", "solution",
        "created_at", "updated_at",
    ])
    for p in items:
        writer.writerow([
            p.get("id"), p.get("week"), p.get("objective"), p.get("task_id"),
            p.get("task_name"), p.get("subtask"), p.get("planned"), p.get("result"),
            p.get("progress_percent"), p.get("issue"), p.get("assignee"),
            p.get("solution"), p.get("created_at"), p.get("updated_at"),
        ])
    output.seek(0)
    return StreamingResponse(
        output,
        media_type="text/csv; charset=utf-8",
        headers={
            "Content-Disposition": "attachment; filename*=UTF-8''progress.csv",
            "Content-Type": "text/csv; charset=utf-8"
        },
    )


# ── CSV import ────────────────────────────────────────────────────────────────

def _parse_csv(content: bytes) -> list[dict]:
    text = content.decode("utf-8-sig")
    reader = csv.DictReader(io.StringIO(text))
    return [row for row in reader]


@router.post("/import/objectives")
async def import_objectives(file: UploadFile = File(...)):
    """Import objectives with key results from CSV."""
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
    """Import tasks from CSV."""
    rows = _parse_csv(await file.read())
    tasks = []
    for r in rows:
        members = []
        members_str = r.get("members", "").strip()
        if members_str:
            for m in members_str.split(";"):
                if "(" in m and ")" in m:
                    name = m.split("(")[0].strip()
                    staff_id = m.split("(")[1].replace(")", "").strip()
                    members.append({"staff_id": staff_id, "name": name})
        tasks.append({
            "id": r.get("task_id") or f"T{str(uuid.uuid4())[:8].upper()}",
            "name": r.get("task_name", "").strip(),
            "objective_id": r.get("objective_id", "").strip(),
            "members": members,
        })
    data_store.save("tasks.json", {"tasks": tasks})
    return {"imported": len(tasks)}


@router.post("/import/staff")
async def import_staff(file: UploadFile = File(...)):
    rows = _parse_csv(await file.read())
    staff = []
    for r in rows:
        staff.append({
            "id": r.get("id") or f"S{str(uuid.uuid4())[:8].upper()}",
            "name": r.get("name", "").strip(),
            "role": r.get("role", "").strip(),
            "main_skills": r.get("main_skills", "").strip(),
            "sub_skills": r.get("sub_skills", "").strip(),
            "learning": r.get("learning", "").strip(),
            "desired_field": r.get("desired_field", "").strip(),
            "objectives": r.get("objectives", "").strip(),
        })
    data_store.save("staff.json", {"staff": staff})
    return {"imported": len(staff)}


@router.post("/import/progress")
async def import_progress(file: UploadFile = File(...)):
    rows = _parse_csv(await file.read())
    today = date.today().isoformat()
    items = []
    for r in rows:
        items.append({
            "id": r.get("id") or f"P{str(uuid.uuid4())[:8].upper()}",
            "week": r.get("week", "").strip(),
            "objective": r.get("objective", "").strip(),
            "task_id": r.get("task_id", "").strip(),
            "task_name": r.get("task_name", "").strip(),
            "subtask": r.get("subtask", "").strip(),
            "planned": r.get("planned", "").strip(),
            "result": r.get("result", "").strip(),
            "progress_percent": int(r.get("progress_percent", 0) or 0),
            "issue": r.get("issue", "").strip(),
            "assignee": r.get("assignee", "").strip(),
            "solution": r.get("solution", "").strip(),
            "created_at": r.get("created_at") or today,
            "updated_at": r.get("updated_at") or today,
        })
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
    if target in ("tasks", "all"):
        data_store.save("tasks.json", {"tasks": []})
    if target in ("staff", "all"):
        data_store.save("staff.json", {"staff": []})
    if target in ("progress", "all"):
        data_store.save("progress.json", {"progress_items": []})
    return {"reset": target}