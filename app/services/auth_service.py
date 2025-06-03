from datetime import timedelta
from sqlalchemy.orm import Session
from app.models.user import User, TokenBlacklist
from app.schemas.auth import UserLogin, UserSignup, Token
from app.schemas.user import UserCreate
from app.services.user_service import UserService
from app.core.security import verify_password, create_access_token, verify_token
from app.core.config import settings
from fastapi import HTTPException, status
from typing import Optional


class AuthService:
    @staticmethod
    def signup(db: Session, user_data: UserSignup) -> dict:
        # Check if user already exists
        existing_user = UserService.get_user_by_email(db, user_data.email)
        print(existing_user)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # Create new user
        user_create = UserCreate(**user_data.model_dump())
        user = UserService.create_user(db, user_create)
        
        # Create access token
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user.email}, expires_delta=access_token_expires
        )
        
        return {
            "user": user,
            "token": Token(
                access_token=access_token,
                expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
            )
        }
    
    @staticmethod
    def login(db: Session, user_data: UserLogin) -> Token:
        # Authenticate user
        user = AuthService.authenticate_user(db, user_data.email, user_data.password)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Create access token
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user.email}, expires_delta=access_token_expires
        )
        
        return Token(
            access_token=access_token,
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
        )
    
    @staticmethod
    def logout(db: Session, token: str) -> dict:
        # Add token to blacklist
        blacklisted_token = TokenBlacklist(token=token)
        db.add(blacklisted_token)
        db.commit()
        
        return {"message": "Successfully logged out"}
    
    @staticmethod
    def authenticate_user(db: Session, email: str, password: str) -> Optional[User]:
        user = UserService.get_user_by_email(db, email)
        if not user:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        return user
    
    @staticmethod
    def is_token_blacklisted(db: Session, token: str) -> bool:
        blacklisted = db.query(TokenBlacklist).filter(TokenBlacklist.token == token).first()
        return blacklisted is not None