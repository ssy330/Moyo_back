# 위쪽에 이미 있을 거라 생각하지만, 혹시 없으면 확인
from pathlib import Path
import os
import uuid
from fastapi import HTTPException, UploadFile

from app.core.paths import PROFILE_DIR, STATIC_DIR

# BASE_DIR / STATIC_DIR / PROFILE_DIR 정의도 이미 있을 거라 가정
# BASE_DIR = Path(__file__).resolve().parent.parent  # app/
# STATIC_DIR = BASE_DIR / "static"
# PROFILE_DIR = STATIC_DIR / "profile"

async def save_profile_image(
    file: UploadFile,
    old_url: str | None = None,
) -> str:
    """프로필 이미지를 저장하고, old_url이 있으면 기존 파일도 삭제"""

    PROFILE_DIR.mkdir(parents=True, exist_ok=True)

    # 1️⃣ 기존 이미지 삭제 (있다면)
    if old_url:
        # '/static/profile/xxx.jpg' 또는 'static/profile/xxx.jpg' 둘 다 처리
        norm = old_url.lstrip("/")  # 앞의 / 제거 → 'static/profile/xxx.jpg'

        if norm.startswith("static/"):
            # 'static/profile/xxx.jpg' → 'profile/xxx.jpg'
            rel_path = norm[len("static/") :]  # 'profile/...'
            old_path = STATIC_DIR / rel_path   # STATIC_DIR/profile/...

            if old_path.is_file():
                try:
                    old_path.unlink()
                except OSError:
                    # 삭제 실패해도 전체 요청은 계속 진행
                    pass

    # 2️⃣ 새 이미지 저장
    filename = file.filename or ""
    _, ext = os.path.splitext(filename)
    ext = ext.lower()

    if ext not in {".jpg", ".jpeg", ".png", ".gif", ".webp"}:
        raise HTTPException(
            status_code=400,
            detail="지원하지 않는 이미지 형식입니다. (jpg, png, gif, webp)",
        )

    new_name = f"{uuid.uuid4().hex}{ext}"
    out_path = PROFILE_DIR / new_name

    content = await file.read()
    with open(out_path, "wb") as f:
        f.write(content)

    # 3️⃣ DB에는 계속 "/static/profile/파일명" 형식으로 저장
    return f"/static/profile/{new_name}"
