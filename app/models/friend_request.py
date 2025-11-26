# app/models/friend_request.py
from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    ForeignKey,
    UniqueConstraint,
    CheckConstraint,
    func,
)
from sqlalchemy.orm import relationship

from app.database import Base


class FriendRequest(Base):
    __tablename__ = "friend_requests"

    id = Column(Integer, primary_key=True, index=True)

    requester_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )

    receiver_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )

    # 어떤 그룹에서 보낸 요청인지(선택)
    group_id = Column(
        Integer,
        ForeignKey("groups.id", ondelete="SET NULL"),
        nullable=True,
    )

    # PENDING / ACCEPTED / REJECTED / CANCELED 등
    status = Column(String(20), nullable=False, default="PENDING")

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # ── 관계 설정 ────────────────────────────────
    requester = relationship(
        "User",
        foreign_keys=[requester_id],
        back_populates="friend_requests_sent",
    )

    receiver = relationship(
        "User",
        foreign_keys=[receiver_id],
        back_populates="friend_requests_received",
    )

    group = relationship(
        "Group",
        back_populates="friend_requests",
    )

    __table_args__ = (
        UniqueConstraint("requester_id", "receiver_id", name="uq_friend_request_pair"),
        CheckConstraint("requester_id <> receiver_id", name="ck_not_self_friend"),
    )
