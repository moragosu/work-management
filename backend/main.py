from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from routers import okrs, progress, staff, admin, tasks, qna, confluence, upload, settings, issues, go, feedback
import uvicorn
import os

UPLOAD_DIR = os.path.join(os.path.dirname(__file__), 'uploads')
os.makedirs(UPLOAD_DIR, exist_ok=True)

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


@app.get("/api/health")
def health_check():
    return {"status": "ok"}


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
