from sqlalchemy import Column, Integer, String, DateTime, Boolean, Enum as SqlEnum, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base
from enum import Enum

class UserRole(str, Enum):
    candidate = "candidate"
    hr = "hr"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    role = Column(SqlEnum(UserRole), default=UserRole.candidate, nullable=False)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class TokenBlacklist(Base):
    __tablename__ = "token_blacklist"
    
    id = Column(Integer, primary_key=True, index=True)
    token = Column(String, unique=True, index=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class HROnboarding(Base):
    __tablename__ = "hr_onboarding"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    company_size = Column(String, nullable=False)
    hiring_timeline = Column(String, nullable=False)
    industry_focus = Column(String, nullable=False)
    user = relationship("User", backref="hr_onboarding", uselist=False)

class UserOnboarding(Base):
    __tablename__ = "user_onboarding"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    career_objectives = Column(String, nullable=False)
    role_interest = Column(String, nullable=False)
    years = Column(String, nullable=False)
    user = relationship("User", backref="user_onboarding", uselist=False)