from datetime import datetime
from typing import Optional
from pydantic import BaseModel

class EventBase(BaseModel):
    title: str
    description: Optional[str] = None
    start_at: datetime
    end_at: datetime
    all_day: bool = False
    group_id: int | None = None

class EventCreate(EventBase):
    pass

class EventUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    start_at: Optional[datetime] = None
    end_at: Optional[datetime] = None
    all_day: Optional[bool] = None

class EventOut(EventBase):
    id: int

    class Config:
        orm_mode = True