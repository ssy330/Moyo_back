from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.database import get_db
from app.schemas.user import UserCreate, UserLogin, SignupOut, LoginOut, EmailRequest, EmailConfirm
from app.services.auth_service import create_user, authenticate_user
from app.utils.security import create_access_token
from app.services.auth_service import request_email_code, confirm_email_code, ensure_recent_verified

router = APIRouter(prefix="/auth", tags=["auth"])

# [신규] 인증코드 발송
@router.post("/email/request")
def email_request(body: EmailRequest, db: Session = Depends(get_db)):
    try:
        request_email_code(db, body.email)
        return {"message": "Verification code sent"}
    except ValueError as e:
        HTTPException(status_code=429, detail=str(e))

# [신규] 인증코드 확인
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
        # [추가] 최근 이메일 인증 성공 이력 확인 (30분이내)
        try:
            ensure_recent_verified(db, body.email, within_minutes=30)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=f"Email not verified: {e}")
        user = create_user(db, body)
        return {"message": "Signup successful", "user_id": user.id}
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Email already registered")

@router.post("/login", response_model=LoginOut)
def login(body: UserLogin, db: Session = Depends(get_db)):
    user = authenticate_user(db, body.email, body.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = create_access_token({"sub": user.email})
    return {"access_token": token, "token_type": "bearer"}
