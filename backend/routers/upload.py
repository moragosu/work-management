from fastapi import APIRouter, UploadFile, File, HTTPException
from PIL import Image
import uuid
import os
import io

router = APIRouter()
DATA_DIR = os.environ.get('DATA_DIR', os.path.join(os.path.dirname(__file__), '..', '..', 'data'))
UPLOAD_DIR = os.path.join(DATA_DIR, 'uploads')
MAX_WIDTH = 1200
MAX_HEIGHT = 1200


@router.post("")
async def upload_file(file: UploadFile = File(...)):
    if not file.content_type or not file.content_type.startswith('image/'):
        raise HTTPException(status_code=400, detail="이미지 파일만 업로드 가능합니다")
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    filename = f"{uuid.uuid4().hex}.png"
    filepath = os.path.join(UPLOAD_DIR, filename)

    data = await file.read()
    img = Image.open(io.BytesIO(data))
    if img.mode not in ("RGB", "RGBA"):
        img = img.convert("RGBA")
    if img.width > MAX_WIDTH or img.height > MAX_HEIGHT:
        img.thumbnail((MAX_WIDTH, MAX_HEIGHT), Image.LANCZOS)
    img.save(filepath, format="PNG", optimize=True)

    return {"url": f"/uploads/{filename}"}


@router.delete("/{filename}")
async def delete_file(filename: str):
    if not filename or '/' in filename or '\\' in filename or '..' in filename:
        raise HTTPException(status_code=400, detail="Invalid filename")
    filepath = os.path.join(UPLOAD_DIR, filename)
    if os.path.isfile(filepath):
        os.remove(filepath)
    return {"ok": True}
