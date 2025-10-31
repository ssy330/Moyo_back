# app/main.py
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.database import Base, engine, get_db
from app import models
from app.routers import auth as auth_router
from app.routers import invites as invites_router
from app.models import invite as _invite_models


# 1) 개발 편의: 모델로 테이블 생성 (운영 전환 시 Alembic 권장)
Base.metadata.create_all(bind=engine)

# 2) 앱 생성 + 문서 경로를 /api/v1 하위로 정리
app = FastAPI(
    title="Auth API Example",
    openapi_url="/api/v1/openapi.json",
    docs_url="/api/v1/docs",
    redoc_url="/api/v1/redoc",
)

# 3) CORS 허용 (프론트 개발 서버)
origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    # 배포 시 프론트 도메인 추가:
    # "https://moyo.vercel.app",
    # "https://your-frontend-domain.com",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,    # 쿠키/세션 사용 시 필요
    allow_methods=["*"],
    allow_headers=["*"],
)

# 4) API 라우터 연결 (버저닝 프리픽스)
app.include_router(auth_router.router, prefix="/api/v1")
app.include_router(invites_router.router, prefix="/api/v1")

# 5) 루트 & 헬스체크
@app.get("/", tags=["system"])
def root():
    return {"ok": True, "message": "Auth API running"}

@app.get("/api/v1/health", tags=["system"])
def health(db: Session = Depends(get_db)):
    db.execute(text("SELECT 1"))
    return {"ok": True, "db": "up"}