# app/schemas/room.py
from datetime import datetime
from pydantic import BaseModel

class RoomBase(BaseModel):
    name: str

class RoomCreate(RoomBase):
    pass

class RoomOut(RoomBase):
    id: int
    created_at: datetime

    class Config:
        orm_mode = True
