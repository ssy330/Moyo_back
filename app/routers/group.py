# app/routers/group_router.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.group import GroupCreate, GroupResponse
from app.services.group_service import create_group
from app.deps.auth import current_user  # 네가 이미 만든 의존성
from app.models.user import User        # User 타입

router = APIRouter(prefix="/groups", tags=["Group"])

@router.post("/", response_model=GroupResponse)
def create_group_api(
    payload: GroupCreate,
    db: Session = Depends(get_db),
    user: User = Depends(current_user),   # 로그인 필수, JWT에서 사용자 읽기
):
    return create_group(db, creator_id=user.id, data=payload)
