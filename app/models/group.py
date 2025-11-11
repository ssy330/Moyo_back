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
)
from sqlalchemy.orm import relationship
from app.database import Base


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
    # 선택: User 모델이 있다면 아래 relationship 유지
    # creator = relationship("User", back_populates="groups")

    # 개인정보 처리방침 동의 여부(감사 추적용)
    privacy_consent = Column(Boolean, nullable=False, default=True)

    # ── 타임스탬프 ─────────────────────────────────────────────
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    # ── 관계 설정 ─────────────────────────────────────────────
    # ✅ BoardRegistry에서 back_populates="group"을 사용 중이므로 반드시 정의 필요
    board_registry = relationship(
        "BoardRegistry",
        back_populates="group",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    # 예: 그룹 내 멤버 관계가 있다면 추가 가능
    # members = relationship("GroupMember", back_populates="group", cascade="all, delete-orphan")

    # 예: 그룹 게시판이나 포스트 등 추가될 수 있는 관계
    # posts = relationship("Post", back_populates="group")
