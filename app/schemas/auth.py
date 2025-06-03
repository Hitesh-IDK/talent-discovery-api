from pydantic import BaseModel, EmailStr
from app.models.user import UserRole


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserSignup(BaseModel):
    name: str
    email: EmailStr
    password: str
    role: UserRole


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int


class TokenData(BaseModel):
    email: str = None


class LogoutResponse(BaseModel):
    message: str