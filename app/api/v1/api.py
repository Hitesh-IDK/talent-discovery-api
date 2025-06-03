from fastapi import APIRouter
from app.api.v1 import auth, resume

api_router = APIRouter()
api_router.include_router(auth.router)
api_router.include_router(resume.router)
