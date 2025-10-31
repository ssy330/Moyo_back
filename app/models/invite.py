# 10/30 생성 신규 파일
# 추가한 이유: 그룹 없이도 코드를 보관/만료/사용제한을 걸 수 있게 범용 엔티티로 설계.
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, Integer, DateTime, func, UniqueConstraint, Text
from datetime import datetime
from app.database import Base

class InviteCode(Base):
    __tablename__ = "invite_codes"
    __table_args__ = (UniqueConstraint("code", name="uq_invite_code"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    code: Mapped[str] = mapped_column(String(16), nullable=False, index=True)  # 예: 8자리
    purpose: Mapped[str] = mapped_column(String(32), nullable=False)           # 예: "GROUP_JOIN"
    payload: Mapped[str | None] = mapped_column(Text)                          # JSON 문자열(선택)
    issuer_user_id: Mapped[int | None] = mapped_column(nullable=True)          # 생성자(선택)
    max_uses: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    used_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    
    # ✅ 파이썬 타입으로 주석(힌트)하고, 실제 컬럼 타입은 오른쪽 mapped_column에 지정
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    revoked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
