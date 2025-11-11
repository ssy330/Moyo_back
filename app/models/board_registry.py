# group ↔ rhymix mid 매핑 !

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Integer, String, ForeignKey, UniqueConstraint
from app.database import Base

class BoardRegistry(Base):
    __tablename__ = "board_registry"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    group_id: Mapped[int] = mapped_column(
        ForeignKey("groups.id", ondelete="CASCADE"), nullable=False, unique=True
    )
    mid: Mapped[str] = mapped_column(String(64), nullable=False, unique=True)

    group = relationship("Group", back_populates="board_registry", passive_deletes=True)

    __table_args__ = (
        UniqueConstraint("group_id", name="uq_board_registry_group"),
        UniqueConstraint("mid", name="uq_board_registry_mid"),
    )
