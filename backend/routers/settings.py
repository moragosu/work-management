from fastapi import APIRouter
from pydantic import BaseModel
from typing import List, Optional
import data_store

router = APIRouter()

SETTINGS_FILE = "settings.json"
DEFAULT_SETTINGS = {
    "task_targets": ["MX", "VD", "DA", "공통"],
    "questioners": [],
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
    task_targets: List[str]
    questioners: Optional[List[str]] = None


@router.put("")
def update_settings(update: SettingsUpdate):
    data = _load()
    data["task_targets"] = [t.strip() for t in update.task_targets if t.strip()]
    if update.questioners is not None:
        data["questioners"] = [q.strip() for q in update.questioners if q.strip()]
    _save(data)
    return data
