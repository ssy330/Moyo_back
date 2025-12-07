# app/scripts/cleanup_static_images.py
from __future__ import annotations

from pathlib import Path
from typing import Set

from app.database import SessionLocal
from app.core.paths import STATIC_DIR  # 이미 쓰고 있던 거 그대로 사용

from app.models.user import User
from app.models.group import Group
from app.models.post import Post

# ⚠️ 이 둘은 실제로 안 써도, mapper 설정 때문에 import 필요함
from app.models.board_registry import BoardRegistry  # noqa: F401
from app.models.room import ChatRoom  # noqa: F401

# 이미지 확장자
IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".gif", ".webp"}

# 디렉터리 설정
BASE_DIR = STATIC_DIR.parent           # app/
PROFILE_DIR = STATIC_DIR / "profile"
GROUP_DIR = STATIC_DIR / "group_images"
POST_DIR = STATIC_DIR / "post_images"

# uploads 는 프로젝트 루트 기준
# 로컬:   Moyo_back/uploads
# 서버:   /app/uploads
UPLOADS_DIR = BASE_DIR.parent / "uploads"


def normalize_db_path(url: str) -> str | None:
    """
    DB에 저장된 url(/static/..., /uploads/..., 전체 URL 등)을
    'static/...' 또는 'uploads/...' 형태로 통일해서 반환.
    """
    if not url:
        return None

    url = url.strip()
    if not url:
        return None

    # 쿼리 스트링 제거
    url = url.split("?", 1)[0]

    # 전체 URL인 경우 path만 추출
    if "://" in url:
        from urllib.parse import urlparse
        path = urlparse(url).path
    else:
        path = url

    path = path.lstrip("/")

    # 이미 static/ 또는 uploads/ 로 시작하면 그대로 사용
    if path.startswith("static/") or path.startswith("uploads/"):
        return path

    # 나머지는 static/ 아래라고 가정
    return f"static/{path}"


def collect_used_paths(session) -> Set[str]:
    """
    DB(User, Group, Post)에 실제로 사용 중인 이미지 경로들을
    'static/...' 또는 'uploads/...' 형태로 모은다.
    """
    used: Set[str] = set()

    # 1) User.profile_image_url
    for u in session.query(User).all():
        p = normalize_db_path(u.profile_image_url)
        if p:
            used.add(p)

    # 2) Group.image_url
    for g in session.query(Group).all():
        p = normalize_db_path(g.image_url)
        if p:
            used.add(p)

    # 3) Post.image_urls (리스트라고 가정)
    for p in session.query(Post).all():
        if not p.image_urls:
            continue
        for url in p.image_urls:
            norm = normalize_db_path(url)
            if norm:
                used.add(norm)

    return used


def iter_image_files(root: Path):
    """root 아래의 모든 이미지 파일(Path)을 yield"""
    if not root.exists():
        return
    for p in root.rglob("*"):
        if p.is_file() and p.suffix.lower() in IMAGE_EXTS:
            yield p


def cleanup_static_images(dry_run: bool = True):
    """
    dry_run=True  → 실제 삭제는 안 하고 무엇을 지울지 출력만
    dry_run=False → 실제 파일 삭제
    """
    session = SessionLocal()
    try:
        used_paths = collect_used_paths(session)
        print(f"✅ DB에서 사용 중인 이미지 경로 수: {len(used_paths)}")

        to_delete: list[Path] = []

        # ───── static/* 쪽 (profile / group_images / post_images) ─────
        static_roots = [PROFILE_DIR, GROUP_DIR, POST_DIR]

        for root in static_roots:
            for file in iter_image_files(root):
                rel = "static/" + file.relative_to(STATIC_DIR).as_posix()
                if rel not in used_paths:
                    to_delete.append(file)

        # ───── uploads/* 쪽 ─────
        for file in iter_image_files(UPLOADS_DIR):
            rel = "uploads/" + file.relative_to(UPLOADS_DIR).as_posix()
            if rel not in used_paths:
                to_delete.append(file)

        print(f"🧹 삭제 대상 파일 개수: {len(to_delete)}")

        for f in to_delete:
            if dry_run:
                print(f"[DRY-RUN] 삭제 예정: {f}")
            else:
                try:
                    f.unlink()
                    print(f"🗑 삭제 완료: {f}")
                except FileNotFoundError:
                    pass

        if dry_run:
            print("\n(※ 현재는 DRY-RUN 이라 실제로 삭제되진 않았어요.)")

    finally:
        session.close()


if __name__ == "__main__":
    import os

    # IMAGE_CLEANUP_APPLY=1 이면 실제 삭제
    apply_flag = os.getenv("IMAGE_CLEANUP_APPLY", "").lower() in ("1", "true", "yes")

    cleanup_static_images(dry_run=not apply_flag)

    if not apply_flag:
        print("\n💡 실제로 지우려면 환경변수 IMAGE_CLEANUP_APPLY=1 을 주고 다시 실행하세요.")
