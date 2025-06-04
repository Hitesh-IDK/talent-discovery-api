from fastapi import UploadFile, HTTPException
from typing import List
from sqlalchemy.orm import Session
from app.models.resume import Resume, ResumeExperience, ResumeEducation, ResumeProject, ResumeCertification, ResumeFile, ResumeFileStatus
from app.schemas.resume import ParsedResume
import json
from groq import Groq
import instructor
from pypdf import PdfReader, PageObject
from app.core.config import settings
import os
from app.utils.resume import getParseMessage
from sentence_transformers import SentenceTransformer
import numpy as np
from sqlalchemy import LargeBinary
from app.utils.embedding import embed_text, cosine_similarity
from app.services.user_service import HROnboardingService

client = Groq(api_key=settings.GROQ_API_KEY)
client = instructor.from_groq(client)

# Load a pre-trained model (do this once at startup)
model = SentenceTransformer('all-MiniLM-L6-v2')

def embed_text(text: str) -> np.ndarray:
    return model.encode([text])[0]

def cosine_similarity(a, b):
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

def parse_single_resume(file: UploadFile) -> ParsedResume:
    try:
        reader = PdfReader(file.file)

        resumeContent = ""

        for page in reader.pages:
            # resume = extract_links(page, resume)
            resumeContent += page.extract_text() + "\n\n"

        messages = getParseMessage(resumeContent)
        response = client.chat.completions.create(
            messages=messages, model="llama-3.3-70b-versatile", temperature=0, response_model=ParsedResume
        )

        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str("Error parsing resume"))
        return None

    # Placeholder for actual parsing logic
    # Return a dummy ParsedResume object for now
    # return ParsedResume(
    #     name="John Doe",
    #     email="john@example.com",
    #     phone="1234567890",
    #     linkedin="https://linkedin.com/in/johndoe",
    #     github="https://github.com/johndoe",
    #     summary="Experienced software engineer.",
    #     experience=[],
    #     education=[],
    #     projects=[],
    #     technical_skills=["Python", "FastAPI"],
    #     soft_skills=["Communication", "Teamwork"],
    #     programming_languages=["Python", "JavaScript"],
    #     languages=["English"],
    #     certifications=[],
    #     total_experience=5.0
    # )

class ResumeService:
    @staticmethod
    def parse_resume(db: Session, resumes: List[UploadFile], user_id: int) -> str:
        for file in resumes:
            parsed: ParsedResume = parse_single_resume(file)
            resume_obj = Resume(
                user_id=user_id,
                name=parsed.name,
                email=parsed.email,
                phone=parsed.phone,
                linkedin=parsed.linkedin,
                github=parsed.github,
                summary=parsed.summary,
                technical_skills=parsed.technical_skills,
                soft_skills=parsed.soft_skills,
                programming_languages=parsed.programming_languages,
                languages=parsed.languages,
                total_experience=parsed.total_experience
            )
            db.add(resume_obj)
            db.flush()  # To get resume_obj.id
            # Experience
            for exp in parsed.experiences:
                db.add(ResumeExperience(
                    resume_id=resume_obj.id,
                    title=exp.title,
                    summary=exp.summary,
                    start_date=exp.start_date,
                    end_date=exp.end_date,
                    organization=exp.organization
                ))
            # Education
            for edu in parsed.educations:
                db.add(ResumeEducation(
                    resume_id=resume_obj.id,
                    title=edu.title,
                    start_date=edu.start_date,
                    end_date=edu.end_date,
                    organization=edu.organization,
                    grade=edu.grade,
                    percentage=edu.percentage
                ))
            # Projects
            for proj in parsed.projects:
                db.add(ResumeProject(
                    resume_id=resume_obj.id,
                    title=proj.title,
                    summary=proj.summary,
                    start_date=proj.start_date,
                    end_date=proj.end_date,
                    technologies=proj.technologies,
                    programming_languages=proj.programming_languages
                ))
            # Certifications
            for cert in parsed.certifications:
                db.add(ResumeCertification(
                    resume_id=resume_obj.id,
                    title=cert.title,
                    organization=cert.organization,
                    end_date=cert.end_date
                ))
            resume_text = f"{parsed.name} {parsed.summary} {' '.join(parsed.technical_skills)} {' '.join(parsed.programming_languages)}"
            embedding = embed_text(resume_text).tolist()
            resume_obj.embedding = embedding
            db.commit()
        return "All resumes parsed and saved successfully."
    
    @staticmethod
    def get_public_resumes(db: Session):
        from app.models.user import User, UserRole
        from app.models.resume import Resume
        candidate_ids = [u.id for u in db.query(User).filter(User.role == UserRole.candidate).all()]
        resumes = db.query(Resume).filter(Resume.user_id.in_(candidate_ids)).all()
        return [
            {
                "id": r.id,
                "user_id": r.user_id,
                "name": r.name,
                "email": r.email,
                "phone": r.phone,
                "linkedin": r.linkedin,
                "github": r.github,
                "summary": r.summary,
                "technical_skills": r.technical_skills,
                "soft_skills": r.soft_skills,
                "programming_languages": r.programming_languages,
                "languages": r.languages,
                "total_experience": r.total_experience
            } for r in resumes
        ]

    @staticmethod
    def get_resumes_by_user(db: Session, user_id: int):
        from app.models.resume import Resume
        resumes = db.query(Resume).filter(Resume.user_id == user_id).all()
        return [
            {
                "id": r.id,
                "user_id": r.user_id,
                "name": r.name,
                "email": r.email,
                "phone": r.phone,
                "linkedin": r.linkedin,
                "github": r.github,
                "summary": r.summary,
                "technical_skills": r.technical_skills,
                "soft_skills": r.soft_skills,
                "programming_languages": r.programming_languages,
                "languages": r.languages,
                "total_experience": r.total_experience
            } for r in resumes
        ]

    @staticmethod
    def get_resume_by_id(db: Session, resume_id: int, current_user):
        from app.models.user import User, UserRole
        from app.models.resume import Resume
        resume = db.query(Resume).filter(Resume.id == resume_id).first()
        if not resume:
            return None, "Resume not found"
        uploader = db.query(User).filter(User.id == resume.user_id).first()
        if not uploader:
            return None, "Uploader not found"
        if uploader.role == UserRole.candidate and current_user.id != uploader.id:
            return None, "Not authorized to access this resume"
        experience = [
            {
                "id": e.id,
                "title": e.title,
                "summary": e.summary,
                "start_date": e.start_date,
                "end_date": e.end_date,
                "organization": e.organization
            } for e in resume.experience
        ]
        education = [
            {
                "id": e.id,
                "title": e.title,
                "start_date": e.start_date,
                "end_date": e.end_date,
                "organization": e.organization,
                "grade": e.grade,
                "percentage": e.percentage
            } for e in resume.education
        ]
        projects = [
            {
                "id": p.id,
                "title": p.title,
                "summary": p.summary,
                "start_date": p.start_date,
                "end_date": p.end_date,
                "technologies": p.technologies,
                "programming_languages": p.programming_languages
            } for p in resume.projects
        ]
        certifications = [
            {
                "id": c.id,
                "title": c.title,
                "organization": c.organization,
                "end_date": c.end_date
            } for c in resume.certifications
        ]
        return {
            "id": resume.id,
            "user_id": resume.user_id,
            "name": resume.name,
            "email": resume.email,
            "phone": resume.phone,
            "linkedin": resume.linkedin,
            "github": resume.github,
            "summary": resume.summary,
            "technical_skills": resume.technical_skills,
            "soft_skills": resume.soft_skills,
            "programming_languages": resume.programming_languages,
            "languages": resume.languages,
            "total_experience": resume.total_experience,
            "experience": experience,
            "education": education,
            "projects": projects,
            "certifications": certifications
        }, None
        
    @staticmethod
    def nlp_search(db: Session, query: str):
        query_vec = embed_text(query)
        resumes = db.query(Resume).filter(Resume.embedding != None).all()
        results = []
        for resume in resumes:
            # Cross-compatible: handle both list (new) and bytes (old)
            if isinstance(resume.embedding, list):
                resume_vec = np.array(resume.embedding, dtype=np.float32)
            else:
                resume_vec = np.frombuffer(resume.embedding, dtype=np.float32)
            score = cosine_similarity(query_vec, resume_vec)
            match_pct = round(float(score) * 100, 2)
            results.append({
                "resume": {
                    "id": resume.id,
                    "user_id": resume.user_id,
                    "name": resume.name,
                    "email": resume.email,
                    "phone": resume.phone,
                    "linkedin": resume.linkedin,
                    "github": resume.github,
                    "summary": resume.summary,
                    "technical_skills": resume.technical_skills,
                    "soft_skills": resume.soft_skills,
                    "programming_languages": resume.programming_languages,
                    "languages": resume.languages,
                    "total_experience": resume.total_experience
                },
                "match": match_pct
            })
        # Sort by match percentage, descending
        results.sort(key=lambda x: x["match"], reverse=True)
        return results[:10]  # Return top 10 matches

    @staticmethod
    def generate_outreach_email(db, resume_id: int, hr_user):
        from app.models.user import UserRole
        if hr_user.role != UserRole.hr:
            raise HTTPException(status_code=403, detail="Not authorized: HR only")
        # Fetch resume
        resume, error = ResumeService.get_resume_by_id(db, resume_id, hr_user)
        if error:
            raise HTTPException(status_code=404, detail=error)
        # Fetch HR onboarding
        hr_onboarding = HROnboardingService.get_onboarding_by_user_id(db, hr_user.id)
        if not hr_onboarding:
            raise HTTPException(status_code=404, detail="HR onboarding data not found")
        # Compose context for Groq
        prompt = f"""
You are an HR professional with the following details:
Name: {hr_user.name}
Email: {hr_user.email}

Company Profile:
Company Size: {hr_onboarding.company_size}
Hiring Timeline: {hr_onboarding.hiring_timeline}
Industry Focus: {hr_onboarding.industry_focus}

You want to reach out to the following candidate:
Name: {resume['name']}
Summary: {resume['summary']}
Technical Skills: {', '.join(resume['technical_skills'])}
Programming Languages: {', '.join(resume['programming_languages'])}
LinkedIn: {resume['linkedin']}
GitHub: {resume['github']}

Write a professional outreach email introducing yourself and your company, and expressing interest in the candidate based on their resume. Be concise, friendly, and relevant to the candidate's background and your company's focus.
"""
        client = Groq(api_key=settings.GROQ_API_KEY)
        response = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama-3.3-70b-versatile",
            temperature=0.7,
            max_tokens=400
        )
        email = response.choices[0].message.content.strip()
        return email

def process_pending_resumes(db: Session):
    pending_files = db.query(ResumeFile).filter(ResumeFile.status == ResumeFileStatus.pending).all()
    for file_record in pending_files:
        try:
            file_record.status = ResumeFileStatus.processing
            db.commit()
            with open(file_record.file_path, "rb") as f:
                # Use UploadFile-like interface for parse_single_resume
                class DummyUploadFile:
                    def __init__(self, file, filename):
                        self.file = file
                        self.filename = filename
                dummy_file = DummyUploadFile(f, os.path.basename(file_record.file_path))
                parsed = parse_single_resume(dummy_file)
            # Save parsed resume (reuse logic from parse_resume)
            resume_obj = Resume(
                user_id=file_record.user_id,
                name=parsed.name,
                email=parsed.email,
                phone=parsed.phone,
                linkedin=parsed.linkedin,
                github=parsed.github,
                summary=parsed.summary,
                technical_skills=parsed.technical_skills,
                soft_skills=parsed.soft_skills,
                programming_languages=parsed.programming_languages,
                languages=parsed.languages,
                total_experience=parsed.total_experience
            )
            db.add(resume_obj)
            db.flush()
            for exp in getattr(parsed, 'experiences', []):
                db.add(ResumeExperience(
                    resume_id=resume_obj.id,
                    title=exp.title,
                    summary=exp.summary,
                    start_date=exp.start_date,
                    end_date=exp.end_date,
                    organization=exp.organization
                ))
            for edu in getattr(parsed, 'educations', []):
                db.add(ResumeEducation(
                    resume_id=resume_obj.id,
                    title=edu.title,
                    start_date=edu.start_date,
                    end_date=edu.end_date,
                    organization=edu.organization,
                    grade=edu.grade,
                    percentage=edu.percentage
                ))
            for proj in getattr(parsed, 'projects', []):
                db.add(ResumeProject(
                    resume_id=resume_obj.id,
                    title=proj.title,
                    summary=proj.summary,
                    start_date=proj.start_date,
                    end_date=proj.end_date,
                    technologies=proj.technologies,
                    programming_languages=proj.programming_languages
                ))
            for cert in getattr(parsed, 'certifications', []):
                db.add(ResumeCertification(
                    resume_id=resume_obj.id,
                    title=cert.title,
                    organization=cert.organization,
                    end_date=cert.end_date
                ))
            resume_text = f"{parsed.name} {parsed.summary} {' '.join(parsed.technical_skills)} {' '.join(parsed.programming_languages)}"
            embedding = embed_text(resume_text).tolist()
            resume_obj.embedding = embedding
            file_record.status = ResumeFileStatus.parsed
            db.commit()
            # Delete the file from storage
            if os.path.exists(file_record.file_path):
                os.remove(file_record.file_path)
        except Exception as e:
            file_record.status = ResumeFileStatus.failed
            db.commit()
