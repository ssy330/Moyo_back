from __future__ import annotations
from datetime import datetime
from enum import Enum
from typing import Optional, List
from pydantic import BaseModel, field_validator, ConfigDict

from app.models.group_member import GroupRole  # 🔥 Enum 그대로 사용


class IdentityMode(str, Enum):
    REALNAME = "REALNAME"
    NICKNAME = "NICKNAME"


class GroupCreate(BaseModel):
    name: str
    description: Optional[str] = None
    image_url: Optional[str] = None     # 파일 업로드 대신 URL부터
    requires_approval: bool = False     # True = 가입 승인, False = 바로 승인
    identity_mode: IdentityMode = IdentityMode.REALNAME
    privacy_consent: bool               # UI상 필수 체크

    @field_validator("privacy_consent")
    @classmethod
    def _must_consent(cls, v):
        if v is not True:
            raise ValueError("개인정보 수집 및 이용에 동의해야 합니다.")
        return v


class GroupResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    image_url: Optional[str]
    requires_approval: bool
    identity_mode: IdentityMode
    creator_id: int
    created_at: datetime
    updated_at: datetime
    member_count: int

    class Config:
        from_attributes = True
        json_encoders = {
            IdentityMode: lambda v: v.value if hasattr(v, "value") else str(v),
        }


# ─────────────────────────────
# 그룹 기본 정보 (디테일/목록 공용)
# ─────────────────────────────
class GroupInfoOut(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    image_url: Optional[str] = None
    requires_approval: bool
    identity_mode: IdentityMode
    creator_id: int
    created_at: datetime
    updated_at: datetime
    member_count: int

    model_config = ConfigDict(from_attributes=True)


# ─────────────────────────────
# 멤버가 참조하는 유저 정보
# ─────────────────────────────
class GroupMemberUserOut(BaseModel):
    id: int
    name: Optional[str] = None
    nickname: Optional[str] = None
    profile_image_url: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


# ─────────────────────────────
# 멤버 정보 + 유저 정보
# ─────────────────────────────
class GroupMemberOut(BaseModel):
    id: int
    group_id: int
    user_id: int
    role: GroupRole             # "OWNER" | "MANAGER" | "MEMBER"
    joined_at: datetime
    updated_at: datetime
    user: Optional[GroupMemberUserOut] = None  # 🔥 여기!

    model_config = ConfigDict(from_attributes=True)


# ─────────────────────────────
# 그룹 디테일 응답
# ─────────────────────────────
class GroupDetailOut(BaseModel):
    group: GroupInfoOut
    members: List[GroupMemberOut]       # 🔥 다시 GroupMemberOut 목록으로!
    boardUrl: Optional[str] = None
    boardMid: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)
