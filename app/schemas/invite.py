# 10/30 생성 신규 파일
from pydantic import BaseModel, Field
from typing import Any, Optional
from datetime import datetime
from pydantic import ConfigDict

class InviteCreateIn(BaseModel):
    purpose: str = Field(..., description="초대 목적. 예: GROUP_JOIN")
    payload: Optional[dict[str, Any]] = Field(default=None, description="추가 데이터")
    # ⬇⬇ [변경] 기본값을 0으로: 0이면 무제한/만료없음
    maxUses: int = Field(0, ge=0, description="0이면 무제한")
    ttlMinutes: int = Field(0, ge=0, description="0이면 만료 없음")

    # ⬇⬇ [추가] Swagger의 Example Value를 무제한 예시로
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "purpose": "GROUP_JOIN",
                "payload": {"groupId": 42},
                "maxUses": 0,          # 무제한
                "ttlMinutes": 0        # 만료 없음
            }
        }
    )

class InviteOut(BaseModel):
    code: str
    purpose: str
    # ⬇⬇ [변경] 무제한이면 None을 내려줄 수 있게
    usesLeft: Optional[int] = None
    expiresAt: Optional[str] = None

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "code": "AB12CD34",
                "purpose": "GROUP_JOIN",
                "usesLeft": None,      # 무제한 표시
                "expiresAt": None
            }
        }
    )

class InviteVerifyIn(BaseModel):
    code: str

class InviteVerifyOut(BaseModel):
    valid: bool
    purpose: str | None = None
    payload: dict | None = None
    usesLeft: int | None = None
    reason: str | None = None

class InviteRedeemIn(BaseModel):
    code: str

# [추가] 재발급(rotate) 유스케이스 추가
class InviteRotateIn(BaseModel):
    code: str
