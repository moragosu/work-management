from fastapi import APIRouter
from pydantic import BaseModel
from typing import List, Optional
import data_store

router = APIRouter()

SETTINGS_FILE = "settings.json"
DEFAULT_SETTINGS = {
    "task_targets": ["MX", "VD", "DA", "공통"],
    "questioners": [],
    "notice": "",
    "dashboard_default_week": "last",
}


def _load() -> dict:
    data = data_store.load(SETTINGS_FILE)
    for k, v in DEFAULT_SETTINGS.items():
        if k not in data:
            data[k] = v
    return data


def _save(data: dict) -> None:
    data_store.save(SETTINGS_FILE, data)


@router.get("")
def get_settings():
    return _load()


class SettingsUpdate(BaseModel):
    task_targets: Optional[List[str]] = None
    questioners: Optional[List[str]] = None
    dashboard_default_week: Optional[str] = None


@router.put("")
def update_settings(update: SettingsUpdate):
    data = _load()
    if update.task_targets is not None:
        data["task_targets"] = [t.strip() for t in update.task_targets if t.strip()]
    if update.questioners is not None:
        data["questioners"] = [q.strip() for q in update.questioners if q.strip()]
    if update.dashboard_default_week in ("this", "last"):
        data["dashboard_default_week"] = update.dashboard_default_week
    _save(data)
    return data


class NoticeUpdate(BaseModel):
    notice: str


@router.get("/notice")
def get_notice():
    return {"notice": _load().get("notice", "")}


@router.put("/notice")
def update_notice(body: NoticeUpdate):
    data = _load()
    data["notice"] = body.notice
    _save(data)
    if body.notice.strip():
        for username in data_store.get_all_usernames():
            data_store.insert_notification(
                username, "notice_updated",
                "파트 공지가 업데이트되었습니다",
                body.notice[:50],
                "/dashboard",
            )
    return {"notice": data["notice"]}
