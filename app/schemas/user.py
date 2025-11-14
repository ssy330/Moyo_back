from pydantic import BaseModel, ConfigDict, EmailStr

class UserCreate(BaseModel):
    email: EmailStr
    name: str
    nickname:str
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

# 🔥 프론트에서 쓸 유저 정보 응답용
class UserOut(BaseModel):
    id: int
    email: EmailStr
    name: str
    nickname: str

    class Config:
        from_attributes = True  # SQLAlchemy 모델 -> Pydantic 변환 허용

# 🔥 회원가입 응답을 프론트 기대에 맞게 변경
class SignupOut(BaseModel):
    access_token: str
    user: UserOut

class LoginOut(BaseModel):
    access_token: str
    token_type: str = "bearer"
    
class EmailRequest(BaseModel):
    email: EmailStr
    
class EmailConfirm(BaseModel):
    email: EmailStr
    code: str
