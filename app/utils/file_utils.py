# app/utils/file_utils.py
from pathlib import Path
import os
import uuid
from fastapi import UploadFile, HTTPException

# app/utils 기준으로 상위가 app 디렉터리
BASE_DIR = Path(__file__).resolve().parent.parent     # app/
STATIC_DIR = BASE_DIR / "static"
PROFILE_DIR = STATIC_DIR / "profile"

async def save_profile_image(file: UploadFile) -> str:
    PROFILE_DIR.mkdir(parents=True, exist_ok=True)

    filename = file.filename or ""
    _, ext = os.path.splitext(filename)
    ext = ext.lower()

    if ext not in {".jpg", ".jpeg", ".png", ".gif", ".webp"}:
        raise HTTPException(status_code=400, detail="지원하지 않는 이미지 형식입니다. (jpg, png, gif, webp)")

    new_name = f"{uuid.uuid4().hex}{ext}"
    out_path = PROFILE_DIR / new_name

    content = await file.read()
    with open(out_path, "wb") as f:
        f.write(content)

    # 🔥 여기서부터는 /static 기준 경로만 리턴
    return f"/static/profile/{new_name}"
