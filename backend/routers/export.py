from fastapi import APIRouter, Query, Depends
from fastapi.responses import PlainTextResponse
import json
import re
import data_store
from dependencies import get_current_user

router = APIRouter()


def _tiptap_to_plain(node: dict, bullet_depth: int = 0) -> str:
    if not node or not isinstance(node, dict):
        return ""
    node_type = node.get("type", "")
    children = node.get("content") or []

    if node_type in ("doc", "blockquote"):
        parts = [_tiptap_to_plain(c, bullet_depth) for c in children]
        return "\n".join(p for p in parts if p)

    elif node_type == "paragraph":
        return "".join(_tiptap_to_plain(c, bullet_depth) for c in children)

    elif node_type == "text":
        return node.get("text", "")

    elif node_type == "hard_break":
        return "\n"

    elif node_type in ("bullet_list", "ordered_list"):
        parts = [_tiptap_to_plain(c, bullet_depth + 1) for c in children]
        return "\n".join(p for p in parts if p)

    elif node_type == "list_item":
        para_text = ""
        sub_texts = []
        for child in children:
            ct = child.get("type", "")
            if ct == "paragraph":
                para_text = _tiptap_to_plain(child, bullet_depth)
            elif ct in ("bullet_list", "ordered_list"):
                sub_texts.append(_tiptap_to_plain(child, bullet_depth))

        if bullet_depth == 1:
            prefix = "  - "
        elif bullet_depth == 2:
            prefix = "    ‧ "
        else:
            prefix = "    " + "  " * (bullet_depth - 2) + "‧ "

        line = prefix + para_text
        if sub_texts:
            line += "\n" + "\n".join(sub_texts)
        return line

    elif node_type == "heading":
        texts = [_tiptap_to_plain(c, bullet_depth) for c in children]
        return "".join(texts)

    else:
        parts = [_tiptap_to_plain(c, bullet_depth) for c in children]
        return "".join(p for p in parts if p)


def _parse_issue_content(raw: str) -> str:
    if not raw:
        return ""
    try:
        node = json.loads(raw)
        if isinstance(node, dict) and node.get("type") == "doc":
            return _tiptap_to_plain(node)
    except (json.JSONDecodeError, TypeError):
        pass
    return re.sub(r"<[^>]+>", "", raw).strip()


def _week_label(week: str) -> str:
    m = re.match(r"(\d{4})-W(\d+)", week)
    return f"{int(m.group(2))}주차" if m else week


@router.get("/available-weeks")
def get_available_weeks(_user=Depends(get_current_user)):
    all_issues = data_store.load("issues.json").get("issues", [])
    weeks = sorted({i.get("week", "") for i in all_issues if i.get("week")}, reverse=True)
    return weeks


@router.get("/weekly-issues", response_class=PlainTextResponse)
def export_weekly_issues(
    weeks: str = Query(..., description="쉼표 구분 주차 e.g. 2025-W20,2025-W21"),
    part_name: str = Query("", description="파트명"),
    _user=Depends(get_current_user),
):
    week_list = [w.strip() for w in weeks.split(",") if w.strip()]
    if not week_list:
        return ""

    all_issues = data_store.load("issues.json").get("issues", [])
    all_tasks  = {t["id"]: t for t in data_store.load("tasks.json").get("tasks", [])}
    all_links  = data_store.load("confluence_links.json").get("links", [])

    # (task_id, week) → [url, ...]
    link_map: dict = {}
    for lnk in all_links:
        key = (lnk.get("task_id", ""), lnk.get("week", ""))
        link_map.setdefault(key, []).append(lnk["url"])

    sections = []
    for week in sorted(week_list, reverse=True):
        week_issues = [i for i in all_issues if i.get("week") == week]
        if not week_issues:
            continue

        # task_id 단위로 묶되 등록 순서 유지
        task_order: list = []
        task_groups: dict = {}
        for iss in sorted(week_issues, key=lambda x: x.get("created_at", "")):
            tid = iss.get("task_id", "")
            if tid not in task_groups:
                task_order.append(tid)
                task_groups[tid] = []
            task_groups[tid].append(iss)

        pname = part_name.strip() or "파트"
        lines = [f"[{_week_label(week)} {pname} 이슈사항]"]

        for tid in task_order:
            task = all_tasks.get(tid, {})
            task_name = task.get("name", tid)

            content_parts = []
            for iss in task_groups[tid]:
                text = _parse_issue_content(iss.get("issue", ""))
                if text:
                    content_parts.append(text)
            merged = "\n".join(content_parts)

            urls = link_map.get((tid, week), [])

            lines.append(f"□ {task_name}")
            if merged:
                lines.append(merged)
            for url in urls:
                lines.append(f"  - 링크 : {url}")
            lines.append("")

        sections.append("\n".join(lines))

    return "\n".join(sections)
