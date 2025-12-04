# app/routers/auth_exchange.py
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
# from app.schemas.auth import TokenOut  # { access_token, refresh_token? }
# from app.security import create_access_token, create_refresh_token  # 네가 쓰던 함수

# --- (선택) Supabase JWT 검증 유틸 ---
import requests, time
import jwt  # PyJWT
from jwt.algorithms import RSAAlgorithm

SUPABASE_PROJECT_REF = "YOUR_PROJECT_REF"  # 예: "abcd1234"
SUPABASE_JWKS_URL = f"https://{SUPABASE_PROJECT_REF}.auth.supabase.co/.well-known/jwks.json"
SUPABASE_ISS = f"https://{SUPABASE_PROJECT_REF}.auth.supabase.co/"

class ExchangeIn(BaseModel):
    supabase_token: str

router = APIRouter(prefix="/auth", tags=["auth"])

def verify_supabase_jwt(token: str) -> dict:
    try:
        # 1) 헤더에서 kid 뽑기
        unverified_header = jwt.get_unverified_header(token)
        kid = unverified_header.get("kid")
        if not kid:
            raise ValueError("Missing kid")

        # 2) JWKS 받아서 해당 kid 키 찾기 (캐싱 권장)
        jwks = requests.get(SUPABASE_JWKS_URL, timeout=5).json()
        key = next((k for k in jwks["keys"] if k["kid"] == kid), None)
        if not key:
            raise ValueError("JWK not found")

        public_key = RSAAlgorithm.from_jwk(key)

        # 3) 검증 (aud는 프로젝트 세팅에 따라 필요할 수 있음)
        payload = jwt.decode(
            token,
            public_key,
            algorithms=["RS256"],
            options={"require": ["exp", "iat", "iss"]},
            issuer=SUPABASE_ISS,
            audience=None,  # 필요 시 설정
        )
        # exp 체크는 decode가 해줌
        return payload
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Invalid Supabase token: {e}")

@router.post("/exchange/supabase", response_model=TokenOut)
def exchange_supabase(inb: ExchangeIn, db: Session = Depends(get_db)):
    # --- 1) Supabase JWT 검증 & 클레임 추출 ---
    payload = verify_supabase_jwt(inb.supabase_token)

    # typical claims: sub, email, email_verified, user_metadata 등
    email = payload.get("email")
    sub = payload.get("sub")
    if not email and not sub:
        raise HTTPException(status_code=400, detail="No identity in supabase token")

    # --- 2) 우리 유저 upsert ---
    user = db.query(User).filter(User.email == email).one_or_none()
    if not user:
        user = User(email=email, name=None, is_active=True)  # 필요 필드 맞춰서
        db.add(user)
        db.commit()
        db.refresh(user)

    # --- 3) 우리 JWT 발급 ---
    access = create_access_token({"sub": user.email})
    refresh = create_refresh_token({"sub": user.email})  # 쓰면 같이 반환

    return {"access_token": access, "refresh_token": refresh}
