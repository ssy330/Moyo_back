from pathlib import Path

# /app/app 기준
BASE_DIR = Path(__file__).resolve().parent.parent  # app/
STATIC_DIR = BASE_DIR / "static"

PROFILE_DIR = STATIC_DIR / "profile"
GROUP_IMG_DIR = STATIC_DIR / "group_images"
POST_IMG_DIR = STATIC_DIR / "post_images"  # 나중에 만들거면

PROFILE_DIR.mkdir(parents=True, exist_ok=True)
GROUP_IMG_DIR.mkdir(parents=True, exist_ok=True)
POST_IMG_DIR.mkdir(parents=True, exist_ok=True)

def delete_static_file(rel_url: str) -> None:
    """
    rel_url: '/static/...' 형태
    """
    if not rel_url:
        return

    # '/static/profile/...' -> 'static/profile/...'
    rel_path = rel_url.lstrip("/")

    file_path = BASE_DIR / rel_path
    if file_path.is_file():
        try:
            file_path.unlink()
        except OSError:
            # 삭제 실패해도 전체 로직은 계속
            pass
