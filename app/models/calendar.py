from datetime import datetime
from sqlalchemy import Column, Enum, Integer, String, Boolean, Text, DateTime, ForeignKey
from sqlalchemy.orm import declarative_base

from app.database import Base  # 기존 Base 사용

class UserEvent(Base):
    __tablename__ = "user_events"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    title = Column(String(200), nullable=False)
    description = Column(Text)

    start_at = Column(DateTime(timezone=True), nullable=False)
    end_at = Column(DateTime(timezone=True), nullable=False)
    all_day = Column(Boolean, nullable=False, default=False)
    
    scope = Column(
    Enum("PERSONAL", "GROUP", name="calendar_event_scope"),
    nullable=False,
    server_default="PERSONAL",
    )
    group_id = Column(Integer, ForeignKey("groups.id"), nullable=True)

    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)