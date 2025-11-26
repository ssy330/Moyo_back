# app/schemas/friend.py
from datetime import datetime
from typing import Optional
from pydantic import BaseModel
from app.schemas.user import UserOut
from app.schemas.group import GroupInfoOut


class FriendRequestCreate(BaseModel):
    receiver_id: int
    group_id: Optional[int] = None


class FriendRequestOut(BaseModel):
    id: int
    status: str
    group_id: Optional[int]
    created_at: datetime

    # 요청 보낸 사람 정보
    requester: UserOut
    group: Optional[GroupInfoOut] = None

    class Config:
        from_attributes = True
