# app/models/group.py
from datetime import datetime
from enum import Enum

from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    Boolean,
    Enum as SAEnum,
    ForeignKey,
    func,
    select,
)
from sqlalchemy.orm import relationship, column_property

from app.database import Base
from app.models.group_member import GroupMember


# ────────────────────────────────────────────────
# 그룹의 실명/닉네임 모드 설정
# ────────────────────────────────────────────────
class IdentityMode(str, Enum):
    REALNAME = "REALNAME"   # 실명만 가능
    NICKNAME = "NICKNAME"   # 닉네임만 가능


# ────────────────────────────────────────────────
# 그룹 모델
# ────────────────────────────────────────────────
class Group(Base):
    __tablename__ = "groups"

    # ── 기본 정보 ─────────────────────────────────────────────
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, nullable=False)
    description = Column(String(255), nullable=True)

    # 썸네일/대표 이미지 URL (파일 업로드는 추후 별도 엔드포인트로)
    image_url = Column(String(255), nullable=True)

    # 가입 승인 방식: True면 관리자 승인 필요(=가입 승인), False면 바로 승인
    requires_approval = Column(Boolean, nullable=False, default=False)

    # 실명/닉네임 모드
    identity_mode = Column(
        SAEnum(IdentityMode, native_enum=False),
        nullable=False,
        default=IdentityMode.REALNAME,
    )

    # ── 생성자 정보 ─────────────────────────────────────────────
    creator_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    creator = relationship(
        "User",
        back_populates="groups_created",
        lazy="joined",
    )

    # ── 멤버십 / 친구 / 보드 매핑 ─────────────────────────────
    members = relationship(
        "GroupMember",
        back_populates="group",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    board_mapping = relationship(
        "BoardRegistry",
        back_populates="group",
        uselist=False,                   # 1:1
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    friend_requests = relationship(
        "FriendRequest",
        back_populates="group",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    # ✅ 게시글 관계: 이 그룹에 속한 게시글들
    posts = relationship(
        "Post",
        back_populates="group",
        cascade="all, delete-orphan",
    )

    # 개인정보 처리방침 동의 여부(감사 추적용)
    privacy_consent = Column(Boolean, nullable=False, default=True)

    # ── 타임스탬프 ─────────────────────────────────────────────
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )

    # ── BoardRegistry 역참조 (기존 구조 유지) ────────────────
    board_registry = relationship(
        "BoardRegistry",
        back_populates="group",
        uselist=False,
        cascade="all, delete-orphan",
    )

    # 🔥 멤버 수 계산용 컬럼
    member_count = column_property(
        select(func.count(GroupMember.id))
        .where(GroupMember.group_id == id)
        .correlate_except(GroupMember)
        .scalar_subquery()
    )
