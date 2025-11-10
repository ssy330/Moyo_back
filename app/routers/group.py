from __future__ import annotations

# ── 표준 라이브러리
import os
from pathlib import Path
import shutil
import uuid

# ── 써드파티
from fastapi import (
    APIRouter,
    Depends,
    Request,
    Response,
    status,
    Form,
    File,
    UploadFile,
)
from sqlalchemy import select, func
from sqlalchemy.orm import Session

# ── 로컬 모듈
from app.database import get_db
from app.deps.auth import current_user
from app.models.group import Group
from app.models.group_member import GroupMember, GroupRole
from app.models.user import User
from app.schemas.group import (
    GroupResponse,
    GroupInfoOut,
    GroupCreate,
    IdentityMode,
)
from app.services.group_service import create_group

from fastapi import HTTPException
import traceback

# ────────────────────────────────────────────────────────────────────────────────
# 라우터 설정
# ────────────────────────────────────────────────────────────────────────────────
router = APIRouter(prefix="/groups", tags=["Group"])

# ✅ 절대 경로 기준으로 변경 (항상 app/static/group_images 안에 저장되도록)
BASE_DIR = Path(__file__).resolve().parent.parent  # app/
STATIC_DIR = BASE_DIR / "static"
UPLOAD_DIR = STATIC_DIR / "group_images"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

# ────────────────────────────────────────────────────────────────────────────────
# POST /groups/
#   - 그룹 생성 (이미지 업로드 포함)
#   - 생성자는 자동으로 OWNER 멤버로 등록됨
# ────────────────────────────────────────────────────────────────────────────────
@router.post("/", response_model=GroupResponse, status_code=status.HTTP_201_CREATED)
def create_group_api(
    response: Response,
    db: Session = Depends(get_db),
    user: User = Depends(current_user),

    name: str = Form(...),
    description: str | None = Form(None),
    requires_approval: bool = Form(False),
    identity_mode: str = Form("REALNAME"),
    privacy_consent: bool = Form(True),
    image: UploadFile | None = File(None),
):
    try:
        image_url = None

        # ① 이미지 업로드 처리
        if image:
            ext = os.path.splitext(image.filename)[1]
            filename = f"{uuid.uuid4().hex}{ext}"
            image_path = os.path.join(UPLOAD_DIR, filename)

            with open(image_path, "wb") as buffer:
                shutil.copyfileobj(image.file, buffer)

            image_url = f"static/group_images/{filename}".replace("\\", "/")

        # ② 스키마에 맞게 Enum 변환
        identity_mode = IdentityMode(identity_mode.upper())

        # ③ 그룹 생성 (서비스 계층이 OWNER 자동 등록)
        g = create_group(
            db,
            creator_id=user.id,
            data=GroupCreate(
                name=name,
                description=description,
                requires_approval=requires_approval,
                identity_mode=identity_mode,
                privacy_consent=privacy_consent,
                image_url=image_url,
            ),
        )

        # ✅ 중복 문제 해결: OWNER 추가 코드를 제거함!
        # (이미 create_group 내부에서 _ensure_owner_membership 호출함)

        # ④ Enum 직렬화 방어
        if hasattr(g.identity_mode, "value"):
            g.identity_mode = g.identity_mode.value

        # ⑤ 응답 헤더 설정
        response.headers["Location"] = f"/groups/{g.id}"

        # ⑥ 안정적 반환
        return GroupResponse.model_validate(g, from_attributes=True)

    except Exception as e:
        import traceback, sys
        print("🔥 [ERROR] 그룹 생성 중 예외 발생!")
        print(traceback.format_exc())
        sys.stdout.flush()
        raise HTTPException(
            status_code=500,
            detail=f"Group creation failed: {type(e).__name__} - {e}",
        )


# ────────────────────────────────────────────────────────────────────────────────
# GET /groups/my
#   - 내가 속한 그룹 목록 + 멤버 수
#   - 이미지 URL 절대경로 변환
# ────────────────────────────────────────────────────────────────────────────────
def to_image_url(request: Request, path: str | None) -> str | None:
    """DB 경로를 절대 URL로 변환"""
    if not path:
        return None

    norm = path.replace("\\", "/")

    # ✅ 이미 절대 URL이면 그대로 반환
    if norm.startswith("http://") or norm.startswith("https://"):
        return norm

    # DB에 static으로 저장된 경우
    if norm.startswith("static/"):
        return str(request.url_for("static", path=norm[len("static/"):]))

    # 그렇지 않으면 static/ 접두어 붙이기
    return str(request.url_for("static", path=norm))


@router.get("/my", response_model=list[GroupInfoOut])
def list_my_groups(
    request: Request,
    db: Session = Depends(get_db),
    user: User = Depends(current_user),
):
    subq = (
        select(
            GroupMember.group_id.label("gid"),
            func.count(GroupMember.id).label("member_count"),
        )
        .group_by(GroupMember.group_id)
        .subquery()
    )

    stmt = (
        select(
            Group,
            func.coalesce(subq.c.member_count, 0).label("member_count"),
        )
        .join(GroupMember, GroupMember.group_id == Group.id)
        .outerjoin(subq, subq.c.gid == Group.id)
        .where(GroupMember.user_id == user.id)
        .order_by(Group.created_at.desc())
    )

    rows = db.execute(stmt).all()

    return [
        GroupInfoOut(
            id=g.id,
            name=g.name,
            description=g.description,
            image_url=to_image_url(request, g.image_url),
            requires_approval=g.requires_approval,
            identity_mode=(
                g.identity_mode
                if isinstance(g.identity_mode, IdentityMode)
                else IdentityMode(str(g.identity_mode).split(".")[-1])
            ),
            creator_id=g.creator_id,
            created_at=g.created_at,
            updated_at=g.updated_at,
            member_count=int(mcount or 0),
        )
        for g, mcount in rows
    ]
