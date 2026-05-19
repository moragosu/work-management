from fastapi import APIRouter
from fastapi.responses import RedirectResponse, JSONResponse
import data_store

router = APIRouter()      # /go/{id}     — 리버스 프록시 직접 접근용 (redirect)
api_router = APIRouter()  # /api/go/{id} — 프론트엔드 GoRedirect 컴포넌트용 (JSON)


def _resolve(link_id: str):
    for q in data_store.load("qna.json").get("questions", []):
        if q["id"] == link_id:
            return f"/progress?week={q['week']}&focusQuestion={link_id}"
    for iss in data_store.load("issues.json").get("issues", []):
        if iss["id"] == link_id:
            return f"/progress?week={iss['week']}&focusIssue={iss['task_id']}"
    return None


@router.get("/{link_id}")
def resolve_short_link(link_id: str):
    url = _resolve(link_id)
    if url:
        return RedirectResponse(url)
    return JSONResponse(status_code=404, content={"detail": "링크를 찾을 수 없습니다"})


@api_router.get("/{link_id}")
def resolve_short_link_json(link_id: str):
    url = _resolve(link_id)
    if url:
        return {"url": url}
    return JSONResponse(status_code=404, content={"detail": "링크를 찾을 수 없습니다"})
