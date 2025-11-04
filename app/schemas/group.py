# app/schemas/group.py
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, HttpUrl, field_validator
from typing import Optional

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

    class Config:
        from_attributes = True  # (Pydantic v2) orm_mode 대체
