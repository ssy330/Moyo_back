# app/services/group_service.py
from sqlalchemy.orm import Session, selectinload, joinedload
from fastapi import HTTPException, status
from datetime import datetime
from sqlalchemy import select, func

from app.models.group import Group, IdentityMode
from app.schemas.group import GroupCreate
from app.models.group_member import GroupMember, GroupRole
from app.schemas.group import GroupDetailOut, GroupInfoOut, GroupMemberOut
from app.services import board_service


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
        .order_by(GroupMember.joined_at.asc(), GroupMember.user_id.asc())
        .limit(limit).offset(offset)
    ).scalars().all()
    return rows

# 내가 속한 그룹 id 목록만 가져오는 헬퍼
def get_my_group_ids(db: Session, user_id: int) -> list[int]:
    """
    user_id가 속한 그룹들의 id 목록만 돌려주는 유틸 함수
    """
    rows = db.execute(
        select(GroupMember.group_id).where(GroupMember.user_id == user_id)
    ).all()
    # rows 는 [(1,), (3,), ...] 이런 형태라서 첫 번째 값만 꺼냄
    return [gid for (gid,) in rows]

# 응답 변환 : 관계를 그대로 사용
def to_group_out(db: Session, group: Group) -> GroupDetailOut:
    """SQLAlchemy Group -> GroupDetailOut 변환"""
    # 1) 상단의 group 정보(단일) 변환
    info = GroupInfoOut.model_validate(group)  # from_attributes=True 기반

    # 2) 멤버 목록 변환 (조인/정렬 필요시 조정)
    members_rows = db.execute(
        select(GroupMember)
        .where(GroupMember.group_id == group.id)
        .order_by(GroupMember.joined_at.asc())
    ).scalars().all()

    members_out = [
        GroupMemberOut(
            user_id=m.user_id,
            role=m.role,
            joined_at=m.joined_at,
        )
        for m in members_rows
    ]

    # 3) Rhymix 게시판 매핑 정보
    out = GroupDetailOut(
        group=info,
        members=members_out,
        boardUrl=None,
        boardMid=None,
    )
    m = board_service.get_mapping(db, group.id)
    if m:
        out.boardMid = m.mid
        out.boardUrl = board_service.build_url(m.mid)

    return out

# 조회 시 관계 로딩 + DTO 변환
def get_group_with_relations(db, group_id: int) -> Group | None:
    stmt = (
        select(Group)
        .where(Group.id == group_id)
        .options(selectinload(Group.board_registry))
    )
    return db.scalar(stmt)