from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from routers import okrs, progress, staff, admin, tasks, qna, confluence, upload, settings, issues, go, feedback
import uvicorn
import os
import data_store

DATA_DIR = os.environ.get('DATA_DIR', os.path.join(os.path.dirname(__file__), '..', 'data'))
UPLOAD_DIR = os.path.join(DATA_DIR, 'uploads')
DIST_DIR = os.path.join(os.path.dirname(__file__), '..', 'dist')
os.makedirs(UPLOAD_DIR, exist_ok=True)

# DB 초기화 (테이블 없으면 생성)
data_store.init_db()

app = FastAPI(title="OKR Management API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(okrs.router, prefix="/api/okrs", tags=["OKRs"])
app.include_router(tasks.router, prefix="/api/tasks", tags=["Tasks"])
app.include_router(progress.router, prefix="/api/progress", tags=["Progress"])
app.include_router(staff.router, prefix="/api/staff", tags=["Staff"])
app.include_router(admin.router, prefix="/api/admin", tags=["Admin"])
app.include_router(qna.router, prefix="/api/qna", tags=["Q&A"])
app.include_router(confluence.router, prefix="/api/confluence", tags=["Confluence"])
app.include_router(upload.router, prefix="/api/upload", tags=["Upload"])
app.include_router(settings.router, prefix="/api/settings", tags=["Settings"])
app.include_router(issues.router, prefix="/api/issues", tags=["Issues"])
app.include_router(feedback.router, prefix="/api/feedback", tags=["Feedback"])
app.include_router(go.router, prefix="/go", tags=["ShortLink"])
app.include_router(go.api_router, prefix="/api/go", tags=["ShortLink"])

app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")

# dist 폴더가 있으면 빌드된 프론트엔드 서빙 (SPA 라우팅 포함)
if os.path.isdir(DIST_DIR):
    app.mount("/assets", StaticFiles(directory=os.path.join(DIST_DIR, "assets")), name="assets")

    @app.get("/api/health")
    def health_check():
        return {"status": "ok"}

    @app.get("/{full_path:path}")
    async def serve_spa(full_path: str):
        file_path = os.path.join(DIST_DIR, full_path)
        if os.path.isfile(file_path):
            return FileResponse(file_path)
        return FileResponse(os.path.join(DIST_DIR, "index.html"))
else:
    @app.get("/api/health")
    def health_check():
        return {"status": "ok"}


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
