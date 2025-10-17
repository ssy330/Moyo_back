from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.database import get_db
from app.schemas.user import UserCreate, UserLogin, SignupOut, LoginOut
from app.services.auth_service import create_user, authenticate_user
from app.utils.security import create_access_token

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/signup", response_model=SignupOut, status_code=201)
def signup(body: UserCreate, db: Session = Depends(get_db)):
    try:
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
