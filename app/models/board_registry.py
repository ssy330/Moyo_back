# group ↔ rhymix mid 매핑 !

from sqlalchemy import Column, Integer, String, DateTime, UniqueConstraint
from sqlalchemy.sql import func
from app.database import Base

class BoardRegistry(Base):
    __tablename__ = "board_registry"

    id = Column(Integer, primary_key=True)
    group_id = Column(Integer, nullable=False, index=True)
    mid = Column(String(100), nullable=False)           # Rhymix 게시판 mid (예: group_42_board)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        UniqueConstraint("group_id", name="uq_board_group"),
        UniqueConstraint("mid", name="uq_board_mid"),
    )
