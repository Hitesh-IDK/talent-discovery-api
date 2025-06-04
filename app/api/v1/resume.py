from fastapi import APIRouter, Depends, HTTPException, status, Form, Query, UploadFile, File, Body
from typing import Annotated
from app.schemas.resume import ResumeParse
from app.services.resume_service import ResumeService
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.api.deps import get_current_user
from app.models.user import User, UserRole
from app.models.resume import ResumeFile, ResumeFileStatus, Resume
import os
from uuid import uuid4
from fastapi.responses import FileResponse
from app.services.user_service import HROnboardingService
from app.core.config import settings
from groq import Groq

router = APIRouter(prefix="/resume", tags=["Resume"])

@router.post("/parse", response_model=dict)
async def parse_resume(
    resume: Annotated[ResumeParse, Form()],
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> dict:
    try:
        result = ResumeService.parse_resume(db, resume.resumes, current_user.id)
        return {
            "message": "Resume parsed successfully",
        }
    except HTTPException as e:
        raise e
    except Exception as e:
        print(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.post("/batch-upload", response_model=dict)
async def batch_upload_resumes(
    resumes: list[UploadFile] = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    upload_dir = os.path.join("assets", "uploaded_resumes")
    os.makedirs(upload_dir, exist_ok=True)
    file_records = []
    for file in resumes:
        ext = os.path.splitext(file.filename)[1]
        unique_name = f"{uuid4().hex}{ext}"
        file_path = os.path.join(upload_dir, unique_name)
        with open(file_path, "wb") as f:
            f.write(await file.read())
        resume_file = ResumeFile(
            user_id=current_user.id,
            file_path=file_path,
            filename=file.filename,
            status=ResumeFileStatus.pending
        )
        db.add(resume_file)
        db.flush()  # get id
        file_records.append({
            "id": resume_file.id,
            "file_path": file_path,
            "filename": file.filename,
            "status": resume_file.status
        })
    db.commit()
    return {"files": file_records}

@router.get("/public", response_model=dict)
def get_public_resumes(db: Session = Depends(get_db)):
    resumes = ResumeService.get_public_resumes(db)
    return {"resumes": resumes}

@router.get("/my-uploads", response_model=dict)
def get_my_uploads(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    files = db.query(ResumeFile).filter(ResumeFile.user_id == current_user.id).all()
    return {"files": [
        {"id": f.id, "file_path": f.file_path, "status": f.status, "user_id": f.user_id, "filename": f.filename} for f in files
    ]}

@router.post("/nlp-search", response_model=dict)
def nlp_search(
    db: Session = Depends(get_db),
    english_query: str = Body(..., embed=True)
):
    results = ResumeService.nlp_search(db, english_query)
    return {"results": results}

@router.get("/private", response_model=dict)
def get_private_resumes(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    resumes = ResumeService.get_resumes_by_user(db, current_user.id)
    return {"resumes": resumes}

@router.post("/outreach-email", response_model=dict)
def generate_outreach_email(
    resume_id: int = Body(..., embed=True),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    email = ResumeService.generate_outreach_email(db, resume_id, current_user)
    return {"email": email}

@router.get("/{resume_id}", response_model=dict)
def get_resume_by_id(resume_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    resume, error = ResumeService.get_resume_by_id(db, resume_id, current_user)
    if error == "Resume not found":
        raise HTTPException(status_code=404, detail=error)
    if error == "Uploader not found":
        raise HTTPException(status_code=404, detail=error)
    if error == "Not authorized to access this resume":
        raise HTTPException(status_code=403, detail=error)
    return resume

