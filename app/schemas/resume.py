from pydantic import BaseModel
from fastapi import UploadFile
from typing import List


class ResumeParse(BaseModel):
    resumes: List[UploadFile]

class ResumeExperience(BaseModel):
    title: str
    summary: str
    start_date: str
    end_date: str
    organization: str

class ResumeEducation(BaseModel):
    title: str
    start_date: str
    end_date: str
    organization: str
    grade: str
    percentage: str

class ResumeProject(BaseModel):
    title: str
    summary: str
    start_date: str
    end_date: str
    technologies: List[str]
    programming_languages: List[str]

class ResumeCertification(BaseModel):
    title: str
    organization: str
    end_date: str

class ParsedResume(BaseModel):
    name: str = ""
    email: str = ""
    phone: str = ""
    linkedin: str = ""
    github: str = ""
    summary: str = ""
    experiences: List[ResumeExperience] = []
    educations: List[ResumeEducation] = []
    projects: List[ResumeProject] = []
    technical_skills: List[str] = []
    soft_skills: List[str] = []
    programming_languages: List[str] = []
    languages: List[str] = []
    certifications: List[ResumeCertification] = []
    total_experience: float = 0.0




