# app/models/group.py
from datetime import datetime
from enum import Enum
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Enum as SAEnum, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base

class IdentityMode(str, Enum):
    REALNAME = "REALNAME"   # 실명만 가능
    NICKNAME = "NICKNAME"   # 닉네임만 가능

class Group(Base):
    __tablename__ = "groups"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, nullable=False)
    description = Column(String(255), nullable=True)

    # 썸네일/대표 이미지 URL (파일 업로드는 추후 별도 엔드포인트로)
    image_url = Column(String(255), nullable=True)

    # 가입 승인 방식: True면 관리자 승인 필요(=가입 승인), False면 바로 승인
    requires_approval = Column(Boolean, nullable=False, default=False)

    # 실명/닉네임 모드
    identity_mode = Column(SAEnum(IdentityMode, native_enum=False), nullable=False, default=IdentityMode.REALNAME)

    # 생성자
    creator_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    # 선택: User 모델이 있다면 아래 relationship 유지
    # creator = relationship("User")

    # 생성 시 동의 체크(감사 추적용)
    privacy_consent = Column(Boolean, nullable=False, default=True)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, nullable=False)
