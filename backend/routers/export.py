from fastapi import APIRouter, Query, Depends
from fastapi.responses import PlainTextResponse
import json
import re
import data_store
from dependencies import get_current_user

router = APIRouter()


# ── Tiptap → plain text ────────────────────────────────────────────────────

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
        return "".join(_tiptap_to_plain(c, bullet_depth) for c in children)
    else:
        parts = [_tiptap_to_plain(c, bullet_depth) for c in children]
        return "".join(p for p in parts if p)


# ── Tiptap → Markdown ──────────────────────────────────────────────────────

def _tiptap_to_markdown(node: dict, bullet_depth: int = 0) -> str:
    if not node or not isinstance(node, dict):
        return ""
    node_type = node.get("type", "")
    children = node.get("content") or []

    if node_type in ("doc", "blockquote"):
        parts = [_tiptap_to_markdown(c, bullet_depth) for c in children]
        return "\n".join(p for p in parts if p)
    elif node_type == "paragraph":
        return "".join(_tiptap_to_markdown(c, bullet_depth) for c in children)
    elif node_type == "text":
        text = node.get("text", "")
        marks = {m.get("type") for m in (node.get("marks") or [])}
        if "bold" in marks:
            text = f"**{text}**"
        if "italic" in marks:
            text = f"*{text}*"
        if "code" in marks:
            text = f"`{text}`"
        return text
    elif node_type == "hard_break":
        return "\n"
    elif node_type in ("bullet_list", "ordered_list"):
        parts = [_tiptap_to_markdown(c, bullet_depth + 1) for c in children]
        return "\n".join(p for p in parts if p)
    elif node_type == "list_item":
        para_text = ""
        sub_texts = []
        for child in children:
            ct = child.get("type", "")
            if ct == "paragraph":
                para_text = _tiptap_to_markdown(child, bullet_depth)
            elif ct in ("bullet_list", "ordered_list"):
                sub_texts.append(_tiptap_to_markdown(child, bullet_depth))
        indent = "  " * (bullet_depth - 1)
        line = f"{indent}- {para_text}"
        if sub_texts:
            line += "\n" + "\n".join(sub_texts)
        return line
    elif node_type == "heading":
        level = node.get("attrs", {}).get("level", 1)
        text = "".join(_tiptap_to_markdown(c, bullet_depth) for c in children)
        return "#" * level + " " + text
    else:
        parts = [_tiptap_to_markdown(c, bullet_depth) for c in children]
        return "".join(p for p in parts if p)


# ── 공통 유틸 ─────────────────────────────────────────────────────────────

def _parse_issue_content(raw: str, fmt: str = "text") -> str:
    if not raw:
        return ""
    try:
        node = json.loads(raw)
        if isinstance(node, dict) and node.get("type") == "doc":
            result = _tiptap_to_markdown(node) if fmt == "markdown" else _tiptap_to_plain(node)
            lines = [l for l in result.split("\n") if l.strip()]
            return "\n".join(lines)
    except (json.JSONDecodeError, TypeError):
        pass
    plain = re.sub(r"<[^>]+>", "", raw).strip()
    lines = [l for l in plain.split("\n") if l.strip()]
    return "\n".join(lines)


def _build_task_name_map(tasks_list: list) -> dict:
    """task_id → 표시 이름 (소과제는 '모과제명 › 소과제명')"""
    m = {}
    for t in tasks_list:
        m[t["id"]] = t.get("name", t["id"])
        for st in (t.get("sub_tasks") or []):
            if not isinstance(st, dict):
                continue
            st_id = st.get("id", "")
            sub_name = st.get("name", "").strip()
            parent_name = t.get("name", t["id"])
            m[st_id] = f"{parent_name} › {sub_name}" if sub_name else f"{parent_name} › {st_id}"
    return m


def _week_label(week: str) -> str:
    m = re.match(r"(\d{4})-W(\d+)", week)
    return f"{int(m.group(2))}주차" if m else week


# ── 엔드포인트 ────────────────────────────────────────────────────────────

@router.get("/available-weeks")
def get_available_weeks(_user=Depends(get_current_user)):
    all_issues = data_store.load("issues.json").get("issues", [])
    weeks = sorted({i.get("week", "") for i in all_issues if i.get("week")}, reverse=True)
    return weeks


@router.get("/weekly-issues", response_class=PlainTextResponse)
def export_weekly_issues(
    weeks: str = Query(..., description="쉼표 구분 주차 e.g. 2025-W20,2025-W21"),
    part_name: str = Query("", description="파트명"),
    fmt: str = Query("text", description="text 또는 markdown"),
    _user=Depends(get_current_user),
):
    week_list = [w.strip() for w in weeks.split(",") if w.strip()]
    if not week_list:
        return ""

    all_issues  = data_store.load("issues.json").get("issues", [])
    tasks_list  = data_store.load("tasks.json").get("tasks", [])
    task_names  = _build_task_name_map(tasks_list)
    all_links   = data_store.load("confluence_links.json").get("links", [])

    link_map: dict = {}
    for lnk in all_links:
        key = (lnk.get("task_id", ""), lnk.get("week", ""))
        link_map.setdefault(key, []).append(lnk["url"])

    is_md = fmt == "markdown"
    sections = []

    for week in sorted(week_list, reverse=True):
        week_issues = [i for i in all_issues if i.get("week") == week]
        if not week_issues:
            continue

        task_order: list = []
        task_groups: dict = {}
        for iss in sorted(week_issues, key=lambda x: x.get("created_at", "")):
            tid = iss.get("task_id", "")
            if tid not in task_groups:
                task_order.append(tid)
                task_groups[tid] = []
            task_groups[tid].append(iss)

        pname = part_name.strip() or "파트"
        header = f"## [{_week_label(week)} {pname} 이슈사항]" if is_md else f"[{_week_label(week)} {pname} 이슈사항]"
        lines = [header]

        for tid in task_order:
            tname = task_names.get(tid, tid)

            content_parts = []
            for iss in task_groups[tid]:
                text = _parse_issue_content(iss.get("issue", ""), fmt)
                if text:
                    content_parts.append(text)
            merged = "\n".join(content_parts)

            urls = link_map.get((tid, week), [])

            if is_md:
                lines.append(f"\n**□ {tname}**")
                if merged:
                    lines.append(merged)
                for url in urls:
                    lines.append(f"- [바로가기]({url})")
            else:
                lines.append(f"\n□ {tname}")
                if merged:
                    lines.append(merged)
                for url in urls:
                    lines.append(f"  - 링크 : {url}")

        sections.append("\n".join(lines))

    return "\n\n".join(sections)
