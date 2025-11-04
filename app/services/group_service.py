# app/services/group_service.py
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from datetime import datetime

from app.models.group import Group, IdentityMode
from app.schemas.group import GroupCreate

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
    return group
