# app/routers/group_router.py
from fastapi import APIRouter, Depends
from fastapi import HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.group import GroupCreate, GroupResponse
from app.services.group_service import create_group
from app.deps.auth import current_user  # 네가 이미 만든 의존성
from app.models.user import User        # User 타입
from app.schemas.group import GroupInfoOut, GroupMemberOut, GroupDetailOut
from app.services.group_service import get_group_with_count, list_group_members

router = APIRouter(prefix="/groups", tags=["Group"])

@router.post("/", response_model=GroupResponse)
def create_group_api(
    payload: GroupCreate,
    db: Session = Depends(get_db),
    user: User = Depends(current_user),   # 로그인 필수, JWT에서 사용자 읽기
):
    return create_group(db, creator_id=user.id, data=payload)

@router.get("/{group_id}", response_model=GroupInfoOut)
def get_group_info_api(
    group_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(current_user),
):
    pair = get_group_with_count(db, group_id)
    if not pair:
        raise HTTPException(status_code=404, detail="GROUP_NOT_FOUND")
    g, count = pair
    return {
        "id": g.id,
        "name": g.name,
        "description": g.description,
        "image_url": g.image_url,
        "requires_approval": g.requires_approval,
        "identity_mode": g.identity_mode,
        "creator_id": g.creator_id,
        "created_at": g.created_at,
        "updated_at": g.updated_at,
        "member_count": count,
    }

@router.get("/{group_id}/members", response_model=list[GroupMemberOut])
def get_group_members_api(
    group_id: int,
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
    user: User = Depends(current_user),
):
    members = list_group_members(db, group_id, limit=limit, offset=offset)
    return [
        {
            "user_id": m.user_id,
            "role": m.role.value if hasattr(m.role, "value") else str(m.role),
            "joined_at": m.joined_at,
        }
        for m in members
    ]
    
#(선택) 상세 한 번에: 정보 + 멤버 20명 (쓸지 말지 고민중이라 일단 넣어둠)
@router.get("/{group_id}/detail", response_model=GroupDetailOut)
def get_group_detail_api(
    group_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(current_user),
):
    pair = get_group_with_count(db, group_id)
    if not pair:
        raise HTTPException(status_code=404, detail="GROUP_NOT_FOUND")
    g, count = pair
    members = list_group_members(db, group_id, limit=20, offset=0)
    return {
        "group": {
            "id": g.id,
            "name": g.name,
            "description": g.description,
            "image_url": g.image_url,
            "requires_approval": g.requires_approval,
            "identity_mode": g.identity_mode,
            "creator_id": g.creator_id,
            "created_at": g.created_at,
            "updated_at": g.updated_at,
            "member_count": count,
        },
        "members": [
            {
                "user_id": m.user_id,
                "role": m.role.value if hasattr(m.role, "value") else str(m.role),
                "joined_at": m.joined_at,
            } for m in members
        ],
    }