from sqlalchemy.orm import Session
from app.models.user import User, HROnboarding, UserOnboarding
from app.schemas.user import UserCreate, HROnboardingCreate, UserOnboardingCreate
from app.core.security import get_password_hash
from typing import Optional


class UserService:
    @staticmethod
    def create_user(db: Session, user_data: UserCreate) -> User:
        hashed_password = get_password_hash(user_data.password)
        db_user = User(
            role=user_data.role,
            name=user_data.name,
            email=user_data.email,
            hashed_password=hashed_password
        )
        
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user
    
    @staticmethod
    def get_user_by_email(db: Session, email: str) -> Optional[User]:
        return db.query(User).filter(User.email == email).first()
    
    @staticmethod
    def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
        return db.query(User).filter(User.id == user_id).first()

class HROnboardingService:
    @staticmethod
    def create_onboarding(db: Session, user_id: int, onboarding_data: HROnboardingCreate) -> HROnboarding:
        onboarding = HROnboarding(
            user_id=user_id,
            company_size=onboarding_data.company_size,
            hiring_timeline=onboarding_data.hiring_timeline,
            industry_focus=onboarding_data.industry_focus
        )
        db.add(onboarding)
        db.commit()
        db.refresh(onboarding)
        return onboarding

    @staticmethod
    def get_onboarding_by_user_id(db: Session, user_id: int) -> HROnboarding:
        return db.query(HROnboarding).filter(HROnboarding.user_id == user_id).first()

class UserOnboardingService:
    @staticmethod
    def create_onboarding(db: Session, user_id: int, onboarding_data: UserOnboardingCreate) -> UserOnboarding:
        onboarding = UserOnboarding(
            user_id=user_id,
            career_objectives=onboarding_data.career_objectives,
            role_interest=onboarding_data.role_interest,
            years=onboarding_data.years
        )
        db.add(onboarding)
        db.commit()
        db.refresh(onboarding)
        return onboarding

    @staticmethod
    def get_onboarding_by_user_id(db: Session, user_id: int) -> UserOnboarding:
        return db.query(UserOnboarding).filter(UserOnboarding.user_id == user_id).first()