from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.auth import UserSignup, UserLogin, Token, LogoutResponse
from app.schemas.user import UserResponse
from app.services.auth_service import AuthService
from app.api.deps import get_current_user, get_current_token
from app.models.user import User

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/signup", response_model=dict)
def signup(
    user_data: UserSignup,
    db: Session = Depends(get_db)
):
    """
    Create a new user account
    """
    try:
        result = AuthService.signup(db, user_data)
        return {
            "message": "User created successfully",
            "user": UserResponse.model_validate(result["user"]),
            "token": result["token"]
        }
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.post("/login", response_model=Token)
def login(
    user_data: UserLogin,
    db: Session = Depends(get_db)
):
    """
    Login user and return access token
    """
    try:
        return AuthService.login(db, user_data)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.post("/logout", response_model=LogoutResponse)
def logout(
    current_user: User = Depends(get_current_user),
    token: str = Depends(get_current_token),
    db: Session = Depends(get_db)
):
    """
    Logout user and blacklist the token
    """
    try:
        result = AuthService.logout(db, token)
        return LogoutResponse(**result)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.get("/me", response_model=UserResponse)
def get_current_user_info(current_user: User = Depends(get_current_user)):
    """
    Get current user information
    """
    return UserResponse.model_validate(current_user)