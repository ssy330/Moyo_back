from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, DateTime, Integer, UniqueConstraint
from datetime import datetime
from app.database import Base

class EmailVerification(Base):
    __tablename__ = "email_verifications"
    __table_args__ = (UniqueConstraint("email", name="uq_email_verifications_email"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    code_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    expires_at: Mapped[datetime]
    verified_at: Mapped[datetime | None]
    last_sent_at: Mapped[datetime | None]
    attempts: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime | None]
