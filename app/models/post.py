# app/models/post.py
from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, func
from sqlalchemy.orm import relationship
from app.database import Base
from app.models.group import Group
from app.models.user import User

class Post(Base):
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True, index=True)
    group_id = Column(Integer, ForeignKey("groups.id"), nullable=False)   # ✅ 그룹
    author_id = Column(Integer, ForeignKey("users.id"), nullable=False)   # ✅ 글쓴이

    title = Column(String(200), nullable=False)
    content = Column(Text, nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    group = relationship(Group, backref="posts")
    author = relationship(User, backref="posts")
