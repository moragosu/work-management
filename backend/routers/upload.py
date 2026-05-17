from fastapi import APIRouter, UploadFile, File, HTTPException
import uuid
import os
import shutil

router = APIRouter()
UPLOAD_DIR = os.path.join(os.path.dirname(__file__), '..', 'uploads')


@router.post("")
async def upload_file(file: UploadFile = File(...)):
    if not file.content_type or not file.content_type.startswith('image/'):
        raise HTTPException(status_code=400, detail="이미지 파일만 업로드 가능합니다")
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    ext = file.filename.rsplit('.', 1)[-1] if file.filename and '.' in file.filename else 'png'
    filename = f"{uuid.uuid4().hex}.{ext}"
    filepath = os.path.join(UPLOAD_DIR, filename)
    with open(filepath, "wb") as f:
        shutil.copyfileobj(file.file, f)
    return {"url": f"/uploads/{filename}"}
