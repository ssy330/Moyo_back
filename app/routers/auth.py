from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.database import get_db
from app.schemas.user import NicknameUpdate, UserCreate, UserLogin, SignupOut, LoginOut, EmailRequest, EmailConfirm
from app.services.auth_service import create_user, authenticate_user
from app.utils.security import create_access_token
from app.services.auth_service import request_email_code, confirm_email_code, ensure_recent_verified
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.utils.security import decode_access_token
from sqlalchemy import select, func
from app.models.user import User
from app.models.group import Group
from fastapi import status

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
         # ⬇ 로그인 때 쓰던 토큰 생성 로직 재사용
        access_token = create_access_token({"sub": user.email})

        # ⬇ 프론트가 기대하는 형태로 응답
        return {
            "access_token": access_token,
            "user": user,
        }
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

# 회원 탈퇴
@router.delete("/me", status_code=status.HTTP_204_NO_CONTENT)
def delete_account(
    creds: HTTPAuthorizationCredentials = Depends(bearer),
    db: Session = Depends(get_db)
):
    if creds is None or creds.scheme.lower() != "bearer":
        raise HTTPException(status_code=401, detail="Missing or invalid token")
    
    try:
        payload = decode_access_token(creds.credentials)
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    email = payload.get("sub")
    user = db.execute(select(User).where(User.email == email)).scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # 방장으로 있는 그룹 수 확인
    owned_group_count = db.scalar(
        select(func.count()).select_from(Group).where(Group.creator_id == user.id)
    )
    
    if owned_group_count and owned_group_count>0:
        raise HTTPException(
            status_code=400,
            detail="방장으로 있는 그룹이 있어서 탈퇴할 수 없습니다. 그룹을 삭제하거나 방장을 위임한 후 다시 시도해 주세요."
        )
    
    db.delete(user)
    db.commit()
    return

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

    return {"id": user.id, "email": user.email, "name": user.name, "nickname":user.nickname, "is_active": user.is_active}

@router.patch("/me/nickname")
def update_nickname(
    body: NicknameUpdate,
    creds: HTTPAuthorizationCredentials = Depends(bearer),
    db: Session = Depends(get_db),
):
    # 토큰 체크
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
        raise HTTPException(status_code=404, detail="User not found")

    # 닉네임 수정
    user.nickname = body.nickname
    db.commit()
    db.refresh(user)

    # /auth/me랑 같은 형태로 돌려주기
    return {
        "id": user.id,
        "email": user.email,
        "name": user.name,
        "nickname": user.nickname,
        "is_active": user.is_active,
    }