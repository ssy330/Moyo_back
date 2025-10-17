# app/utils/security.py
import os, datetime as dt
import jwt  # PyJWT
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# 비밀번호 해시/검증
def hash_password(pw: str) -> str:
    return pwd_context.hash(pw)

def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)

# JWT 설정
JWT_SECRET = os.getenv("JWT_SECRET", "dev-secret")
JWT_ALG = os.getenv("JWT_ALG", "HS256")
JWT_EXPIRE_MIN = int(os.getenv("JWT_EXPIRE_MIN", "60"))

def create_access_token(claims: dict) -> str:
    now = dt.datetime.utcnow()
    exp = now + dt.timedelta(minutes=JWT_EXPIRE_MIN)
    to_encode = {**claims, "iat": now, "nbf": now, "exp": exp}
    return jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALG)

def decode_access_token(token: str) -> dict:
    return jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALG])
