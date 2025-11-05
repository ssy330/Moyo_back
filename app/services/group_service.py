# app/services/group_service.py
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from datetime import datetime
from sqlalchemy import select, func

from app.models.group import Group, IdentityMode
from app.schemas.group import GroupCreate
from app.models.group_member import GroupMember, GroupRole

# [추가]
def _ensure_owner_membership(db: Session, group: Group, creator_id: int):
    """그룹 생성 직후, 생성자를 OWNER로 멤버 테이블에 보장"""
    exists = db.scalar(
        select(GroupMember.id).where(
            GroupMember.group_id == group.id,
            GroupMember.user_id == creator_id,
        )
    )
    if not exists:
        db.add(GroupMember(group_id=group.id, user_id=creator_id, role=GroupRole.OWNER))
        db.commit()

# [변경] create_group 끝에 OWNER 보장 한 줄 추가
def create_group(db: Session, creator_id: int, data: GroupCreate) -> Group:
    # 중복 이름 체크
    exists = db.query(Group).filter(Group.name == data.name).first()
    if exists:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="이미 존재하는 그룹 이름입니다.")

    group = Group(
        name=data.name.strip(),
        description=(data.description or "").strip() or None,
        image_url=data.image_url,
        requires_approval=data.requires_approval,
        identity_mode=IdentityMode(data.identity_mode),
        creator_id=creator_id,
        privacy_consent=True,  # validator로 강제되므로 True
    )
    db.add(group)
    db.commit()
    db.refresh(group)
    _ensure_owner_membership(db, group, creator_id=creator_id)  # [추가]
    return group

# [신규] 그룹 단건 + 멤버수
def get_group_with_count(db: Session, group_id: int) -> tuple[Group, int] | None:
    g = db.scalar(select(Group).where(Group.id == group_id))
    if not g:
        return None
    cnt = db.scalar(select(func.count()).select_from(GroupMember).where(GroupMember.group_id == group_id)) or 0
    return g, cnt

# [신규] 멤버 리스트(페이징)
def list_group_members(db: Session, group_id: int, limit: int = 50, offset: int = 0):
    rows = db.execute(
        select(GroupMember)
        .where(GroupMember.group_id == group_id)
        .order_by(GroupMember.joined_at.asc())
        .limit(limit).offset(offset)
    ).scalars().all()
    return rows