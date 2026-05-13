from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import StreamingResponse
import csv
import io
import json
import uuid
from datetime import date
import data_store

router = APIRouter()


# ── CSV export ────────────────────────────────────────────────────────────────

@router.get("/export/objectives")
def export_objectives():
    """Export objectives with key results as CSV."""
    objectives = data_store.load("okrs.json").get("objectives", [])
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([
        "objective_id", "objective_name", "pl", "tech_stack", "status",
        "kr_id", "kr_name", "kr_progress"
    ])
    for o in objectives:
        key_results = o.get("key_results", [])
        if key_results:
            for kr in key_results:
                writer.writerow([
                    o.get("id"), o.get("name"), o.get("pl"),
                    o.get("tech_stack"), o.get("status"),
                    kr.get("id"), kr.get("name"), kr.get("progress"),
                ])
        else:
            writer.writerow([
                o.get("id"), o.get("name"), o.get("pl"),
                o.get("tech_stack"), o.get("status"),
                "", "", "",
            ])
    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=objectives.csv"},
    )


@router.get("/export/staff")
def export_staff():
    staff = data_store.load("staff.json").get("staff", [])
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["id", "name", "role", "main_skills", "sub_skills", "learning", "desired_field", "objectives"])
    for s in staff:
        writer.writerow([
            s.get("id"), s.get("name"), s.get("role"),
            s.get("main_skills"), s.get("sub_skills"),
            s.get("learning"), s.get("desired_field"), s.get("objectives"),
        ])
    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=staff.csv"},
    )


@router.get("/export/progress")
def export_progress():
    items = data_store.load("progress.json").get("progress_items", [])
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([
        "id", "week", "objective", "task", "subtask", "planned",
        "result", "progress_percent", "issue", "assignee", "solution",
        "created_at", "updated_at",
    ])
    for p in items:
        writer.writerow([
            p.get("id"), p.get("week"), p.get("objective"), p.get("task"),
            p.get("subtask"), p.get("planned"), p.get("result"),
            p.get("progress_percent"), p.get("issue"), p.get("assignee"),
            p.get("solution"), p.get("created_at"), p.get("updated_at"),
        ])
    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=progress.csv"},
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
                "pl": r.get("pl", "").strip(),
                "team_members": [],
                "tech_stack": r.get("tech_stack", "").strip(),
                "key_results": [],
                "status": r.get("status", "진행중").strip(),
            }
        
        kr_id = r.get("kr_id", "").strip()
        if kr_id:
            objectives_map[obj_id]["key_results"].append({
                "id": kr_id,
                "name": r.get("kr_name", "").strip(),
                "progress": int(r.get("kr_progress", 0) or 0),
            })
    
    objectives = list(objectives_map.values())
    data_store.save("okrs.json", {"objectives": objectives})
    return {"imported": len(objectives)}


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
            "task": r.get("task", "").strip(),
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
    allowed = {"objectives", "staff", "progress", "all"}
    if target not in allowed:
        raise HTTPException(status_code=400, detail=f"target must be one of {allowed}")
    if target in ("objectives", "all"):
        data_store.save("okrs.json", {"objectives": []})
    if target in ("staff", "all"):
        data_store.save("staff.json", {"staff": []})
    if target in ("progress", "all"):
        data_store.save("progress.json", {"progress_items": []})
    return {"reset": target}


# ── Backward compatibility aliases ─────────────────────────────────────────────

@router.get("/export/okrs")
def export_okrs_alias():
    """Alias for backward compatibility."""
    return export_objectives()


@router.post("/import/okrs")
async def import_okrs_alias(file: UploadFile = File(...)):
    """Alias for backward compatibility."""
    return await import_objectives(file)