# app/schemas/room.py
from datetime import datetime
from pydantic import BaseModel, ConfigDict

class RoomBase(BaseModel):
    name: str

class RoomCreate(RoomBase):
    pass

class RoomGroupOut(BaseModel):
    id: int
    name: str
    image_url: str | None = None

    class Config:
        model_config = ConfigDict(from_attributes=True)

class RoomOut(RoomBase):
    id: int
    created_at: datetime
    group: RoomGroupOut | None = None
    
    last_message_content: str | None = None
    last_message_created_at: datetime | None = None

    class Config:
        model_config = ConfigDict(from_attributes=True)
