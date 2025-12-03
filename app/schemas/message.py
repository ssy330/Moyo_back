# app/schemas/message.py
from datetime import datetime
from pydantic import BaseModel, ConfigDict

class MessageBase(BaseModel):
    content: str

class MessageCreate(MessageBase):
    room_id: int

class MessageOut(MessageBase):
    id: int
    room_id: int
    user_id: int | None
    created_at: datetime
    user_nickname: str | None = None 

    class Config:
        model_config = ConfigDict(from_attributes=True)
