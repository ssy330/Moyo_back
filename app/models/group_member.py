# [신규]
from datetime import datetime, timezone
from enum import Enum
from sqlalchemy import Column, Integer, DateTime, ForeignKey, Enum as SAEnum, UniqueConstraint, Index
from sqlalchemy.orm import relationship
from app.database import Base

class GroupRole(str, Enum):
    OWNER = "OWNER"
    MANAGER = "MANAGER"
    MEMBER = "MEMBER"

class GroupMember(Base):
    __tablename__ = "group_members"

    id = Column(Integer, primary_key=True)
    group_id = Column(Integer, ForeignKey("groups.id", ondelete="CASCADE"), index=True, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    role = Column(SAEnum(GroupRole, native_enum=False), nullable=False, default=GroupRole.MEMBER)
    
    # (변경) UTC aware + 자동 갱신
    joined_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc),
                        onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    __table_args__ = (
        UniqueConstraint("group_id", "user_id", name="uq_group_member"),
        # (추가) 목록 조회 + 정렬 최적화용 복합 인덱스
        Index("ix_group_members_gid_joined_at", "group_id", "joined_at"),
        # 필요시 안정 정렬까지 고려한다면 ↓(선택) - 혹시 모르니 지우지 않고 두겠음
        # Index("ix_group_members_gid_joined_at_uid", "group_id", "joined_at", "user_id"),
    )
