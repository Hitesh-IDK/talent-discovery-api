from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional
from app.models.user import UserRole


class UserBase(BaseModel):
    name: str
    email: EmailStr
    role: UserRole


class UserCreate(UserBase):
    password: str


class UserResponse(UserBase):
    id: int
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


class UserInDB(UserBase):
    id: int
    hashed_password: str
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


class HROnboardingBase(BaseModel):
    company_size: str
    hiring_timeline: str
    industry_focus: str


class HROnboardingCreate(HROnboardingBase):
    pass


class HROnboardingResponse(HROnboardingBase):
    id: int
    user_id: int
    class Config:
        from_attributes = True


class UserOnboardingBase(BaseModel):
    career_objectives: str
    role_interest: str
    years: str


class UserOnboardingCreate(UserOnboardingBase):
    pass


class UserOnboardingResponse(UserOnboardingBase):
    id: int
    user_id: int
    class Config:
        from_attributes = True