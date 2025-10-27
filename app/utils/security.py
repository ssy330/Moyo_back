# app/utils/security.py
import os, datetime as dt, hashlib, hmac, random, smtplib
import jwt  # PyJWT
from passlib.context import CryptContext
from email.message import EmailMessage

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

# 이메일 인증 코드 관련
EMAIL_SECRET = os.getenv("EMAIL_SECRET", "dev-email-secret")  # 코드 해시 pepper
SMTP_HOST = os.getenv("SMTP_HOST", "")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER", "")
SMTP_PASS = os.getenv("SMTP_PASS", "")
SMTP_FROM = os.getenv("SMTP_FROM", SMTP_USER or "noreply@example.com")

def create_access_token(claims: dict) -> str:
    now = dt.datetime.utcnow()
    exp = now + dt.timedelta(minutes=JWT_EXPIRE_MIN)
    to_encode = {**claims, "iat": now, "nbf": now, "exp": exp}
    return jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALG)

def decode_access_token(token: str) -> dict:
    return jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALG])

def gen_code(length: int = 6) -> str:
    # 000000~999999, 앞자리 0 유지
    return f"{random.randint(0, 999999):06d}"

def hash_code(code: str) -> str:
    return hmac.new(EMAIL_SECRET.encode(), code.encode(), hashlib.sha256).hexdigest()

def verify_code(code: str, code_hash: str) -> bool:
    return hmac.compare_digest(hash_code(code), code_hash)

def send_email_code(to_email: str, code: str):
    """SMTP가 없으면 개발 모드로 콘솔에만 출력."""
    subject = "[Moyo] 이메일 인증코드"
    body = f"인증코드: {code}\n10분 이내에 입력해 주세요."
    if not SMTP_HOST:
        print(f"[DEV EMAIL] to={to_email} code={code}")
        return
    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = SMTP_FROM
    msg["To"] = to_email
    msg.set_content(body)
    with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as s:
        s.starttls()
        if SMTP_USER:
            s.login(SMTP_USER, SMTP_PASS)
        s.send_message(msg)