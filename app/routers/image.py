# app/routers/image.py
from fastapi import APIRouter, UploadFile, File
from fastapi.responses import JSONResponse
from pathlib import Path
import uuid

router = APIRouter(prefix="/images", tags=["images"])

# ─────────────────────────────
# 1) static/post_images 경로 설정
# ─────────────────────────────
# 현재 파일 기준으로 app 디렉토리 찾기
APP_DIR = Path(__file__).resolve().parents[1]
STATIC_DIR = APP_DIR / "static"
POST_IMAGES_DIR = STATIC_DIR / "post_images"

# 폴더 없으면 생성
POST_IMAGES_DIR.mkdir(parents=True, exist_ok=True)


@router.post("/upload")
async def upload_image(file: UploadFile = File(...)):
    # 확장자 유지 (.png, .jpg 등)
    ext = Path(file.filename).suffix
    filename = f"{uuid.uuid4().hex}{ext}"
    save_path = POST_IMAGES_DIR / filename

    # 파일 저장
    contents = await file.read()
    with save_path.open("wb") as f:
        f.write(contents)

    # ✅ 이제는 /static/post_images/ 경로로 URL 반환
    url = f"/static/post_images/{filename}"

    return JSONResponse({"url": url})
