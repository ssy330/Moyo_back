from sqlalchemy import Column, Integer, String, Boolean, DateTime, func
from sqlalchemy.orm import relationship
from app.database import Base
from app.models.friend_request import FriendRequest

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    name = Column(String(100), nullable=False)
    nickname = Column(String(100), nullable=False)
    hashed_password = Column(String(255), nullable=False) 
    is_active = Column(Boolean, nullable=False, server_default="1")
    
     # 프로필 이미지 URL (예: "/static/profile/xxx.png")
    profile_image_url = Column(String(255), nullable=True)
    
    # 역참조
    groups_created = relationship("Group", back_populates="creator")
    group_memberships = relationship("GroupMember", back_populates="user", cascade="all, delete-orphan")
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    friend_requests_sent = relationship(
        "FriendRequest",
        foreign_keys=[FriendRequest.requester_id],
        back_populates="requester",
        cascade="all, delete-orphan",
    )
    friend_requests_received = relationship(
        "FriendRequest",
        foreign_keys=[FriendRequest.receiver_id],
        back_populates="receiver",
        cascade="all, delete-orphan",
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )