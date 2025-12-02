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

# 🔥 친구 목록용 응답
class FriendOut(BaseModel):
    id: int                      # friend_request id 그대로 써도 됨
    created_at: datetime         # 친구가 된 시점 (요청 생성/수락 시점)
    friend: UserOut              # "상대방" 유저
    group: Optional[GroupInfoOut] = None  # 어떤 그룹에서 연결됐는지 (있다면)

    class Config:
        arbitrary_types_allowed = True

class FriendUser(BaseModel):
    id: int
    email: str
    name: str
    nickname: str
    profile_image_url: str | None = None

    class Config:
        from_attributes = True  # pydantic v2 (orm_mode 대체)


class FriendListGroup(BaseModel):
    id: int
    name: str
    image_url: str | None = None

    class Config:
        from_attributes = True


class OutgoingFriendRequestOut(BaseModel):
    id: int
    status: str
    group_id: int | None = None
    created_at: datetime
    receiver: FriendUser
    group: FriendListGroup | None = None

    class Config:
        from_attributes = True