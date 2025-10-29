from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.database import get_db
from app.schemas.user import UserCreate, UserLogin, SignupOut, LoginOut, EmailRequest, EmailConfirm
from app.services.auth_service import create_user, authenticate_user
from app.utils.security import create_access_token
from app.services.auth_service import request_email_code, confirm_email_code, ensure_recent_verified
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.utils.security import decode_access_token
from sqlalchemy import select
from app.models.user import User

router = APIRouter(prefix="/auth", tags=["auth"])

# Bearer 인증 디펜던시
bearer = HTTPBearer(auto_error=False)

# 인증코드 발송
@router.post("/email/request")
def email_request(body: EmailRequest, db: Session = Depends(get_db)):
    try:
        request_email_code(db, body.email)
        return {"message": "Verification code sent"}
    except ValueError as e:
        # FIX: raise 누락되어 있어서 추가
        raise HTTPException(status_code=429, detail=str(e))

# 인증코드 확인
@router.post("/email/confirm")
def email_confirm(body: EmailConfirm, db: Session = Depends(get_db)):
    try:
        confirm_email_code(db, body.email, body.code)
        return {"verified": True}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/signup", response_model=SignupOut, status_code=201)
def signup(body: UserCreate, db: Session = Depends(get_db)):
    try:
        # 최근 이메일 인증 성공 이력 확인 (30분이내)
        try:
            ensure_recent_verified(db, body.email, within_minutes=30)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=f"Email not verified: {e}")
        user = create_user(db, body)
        return {"message": "Signup successful", "user_id": user.id}
    except IntegrityError:
        db.rollback()
        # FIX: 중복 이메일은 409가 표준 (400 -> 409로 수정)
        raise HTTPException(status_code=409, detail="Email already registered")

@router.post("/login", response_model=LoginOut)
def login(body: UserLogin, db: Session = Depends(get_db)):
    user = authenticate_user(db, body.email, body.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = create_access_token({"sub": user.email})
    return {"access_token": token, "token_type": "bearer"}

# [신규] 보호 라우트: 현재 로그인 사용자 정보
@router.get("/me")
def me(
    creds: HTTPAuthorizationCredentials = Depends(bearer),
    db: Session = Depends(get_db),
):
    if creds is None or creds.scheme.lower() != "bearer":
        raise HTTPException(status_code=401, detail="Missing or invalid token")
    try:
        payload = decode_access_token(creds.credentials)
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")
    email = payload.get("sub")
    if not email:
        raise HTTPException(status_code=401, detail="Invalid token")

    user = db.execute(select(User).where(User.email == email)).scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    return {"id": user.id, "email": user.email, "name": user.name, "is_active": user.is_active}