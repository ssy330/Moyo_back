# group ↔ rhymix mid 매핑 !
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Column, Integer, String, ForeignKey, UniqueConstraint
from app.database import Base

class BoardRegistry(Base):
    __tablename__ = "board_registry"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    group_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("groups.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        unique=True,        # ← 그룹당 1개만 매핑되도록
    )

    mid: Mapped[str] = mapped_column(String(80), nullable=False, unique=True)  # rhymix MID 전역 유니크

    # 관계는 "한 번"만 선언, Group 쪽의 속성과 정확히 매칭
    group = relationship("Group", back_populates="board_registry", passive_deletes=True)
    

    __table_args__ = (
        UniqueConstraint("group_id", name="uq_board_registry_group"),
        UniqueConstraint("mid", name="uq_board_registry_mid"),
    )
