from pydantic import BaseModel, EmailStr

class UserCreate(BaseModel):
    email: EmailStr
    name: str
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class SignupOut(BaseModel):
    message: str
    user_id: int

class LoginOut(BaseModel):
    access_token: str
    token_type: str = "bearer"
    
class EmailRequest(BaseModel):
    email: EmailStr
    
class EmailConfirm(BaseModel):
    email: EmailStr
    code: str
