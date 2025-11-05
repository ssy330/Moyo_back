# [신규]
from datetime import datetime
from enum import Enum
from sqlalchemy import Column, Integer, DateTime, ForeignKey, Enum as SAEnum, UniqueConstraint
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
    joined_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    __table_args__ = (
        UniqueConstraint("group_id", "user_id", name="uq_group_member"),
    )
