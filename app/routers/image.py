# app/routers/image.py
from fastapi import APIRouter, UploadFile, File
from fastapi.responses import JSONResponse
from pathlib import Path
import uuid

router = APIRouter(prefix="/images", tags=["images"])

# 업로드 폴더 (프로젝트 루트 기준)
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


@router.post("/upload")
async def upload_image(file: UploadFile = File(...)):
    # 확장자 유지
    ext = Path(file.filename).suffix  # ".png" 이런 거
    filename = f"{uuid.uuid4().hex}{ext}"
    save_path = UPLOAD_DIR / filename

    # 파일 저장
    with save_path.open("wb") as f:
        f.write(await file.read())

    # 정적 파일 URL (아래 mount랑 맞추기)
    url = f"/uploads/{filename}"

    return JSONResponse({"url": url})
