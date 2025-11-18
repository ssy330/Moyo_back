# app/models/message.py
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, func
from sqlalchemy.orm import relationship
from app.database import Base

class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    room_id = Column(Integer, ForeignKey("chat_rooms.id", ondelete="CASCADE"))
    user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"))
    content = Column(String, nullable=False)
    created_at = Column(DateTime, server_default=func.now())

    room = relationship("ChatRoom", back_populates="messages")
    user = relationship("User")
