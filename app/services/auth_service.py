from sqlalchemy.orm import Session
from app.models.user import User
from app.schemas.user import UserCreate
from app.utils.security import hash_password, verify_password
from fastapi import HTTPException
from datetime import datetime, timedelta
from sqlalchemy import select
from app.models.email_verification import EmailVerification
from app.utils.security import gen_code, hash_code, verify_code, send_email_code

def create_user(db: Session, data: UserCreate) -> User:
    email = data.email.lower().strip()
    existing = db.query(User).filter(User.email == email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    user = User(
        email=email,
        name=data.name,
        hashed_password=hash_password(data.password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def authenticate_user(db: Session, email: str, password: str) -> User | None:
    user = db.query(User).filter(User.email == email.lower().strip()).first()
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user

# 이메일 코드 요청
def request_email_code(db: Session, email: str) -> None:
    now = datetime.utcnow()
    ev = db.execute(select(EmailVerification).where(EmailVerification.email == email)).scalar_one_or_none()
    # 60초 이내 재요청 제한
    if ev and ev.last_sent_at and (now - ev.last_sent_at).total_seconds() < 60:
        raise ValueError("Too many requests. Please wait a moment.")
    code = gen_code()
    code_h = hash_code(code)
    expires = now + timedelta(minutes=10)
    if ev:
        ev.code_hash = code_h
        ev.expires_at = expires
        ev.verified_at = None
        ev.last_sent_at = now
        ev.attempts = 0
    else:
        ev = EmailVerification(email=email, code_hash=code_h, expires_at=expires, last_sent_at=now, attempts=0)
        db.add(ev)
    db.commit()
    send_email_code(email, code)  # 커밋 후 발송

# 이메일 코드 확인
def confirm_email_code(db: Session, email: str, code: str) -> None:
    ev = db.execute(select(EmailVerification).where(EmailVerification.email == email)).scalar_one_or_none()
    if not ev:
        raise ValueError("Code not found")
    now = datetime.utcnow()
    if ev.expires_at < now:
        raise ValueError("Code expired")
    if ev.attempts >= 5:
        raise ValueError("Too many attempts")
    ev.attempts += 1
    if not verify_code(code, ev.code_hash):
        db.commit()
        raise ValueError("Invalid code")
    ev.verified_at = now
    db.commit()

def ensure_recent_verified(db: Session, email: str, within_minutes: int = 30) -> None:
    """회원가입 직전에 최근 인증 성공 이력이 있어야 가입 허용."""
    ev = db.execute(select(EmailVerification).where(EmailVerification.email == email)).scalar_one_or_none()
    if not ev or not ev.verified_at:
        raise ValueError("Email not verified")
    if ev.verified_at < datetime.utcnow() - timedelta(minutes=within_minutes):
        raise ValueError("Verification expired")