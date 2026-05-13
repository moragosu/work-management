from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import okrs, progress, staff, admin
import uvicorn

app = FastAPI(title="OKR Management API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(okrs.router, prefix="/api/okrs", tags=["OKRs"])
app.include_router(progress.router, prefix="/api/progress", tags=["Progress"])
app.include_router(staff.router, prefix="/api/staff", tags=["Staff"])
app.include_router(admin.router, prefix="/api/admin", tags=["Admin"])


@app.get("/api/health")
def health_check():
    return {"status": "ok"}


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
