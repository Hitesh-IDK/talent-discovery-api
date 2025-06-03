from sqlalchemy import Column, Integer, String, Float, ForeignKey, Text, Enum as SqlEnum, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import JSONB
from app.core.database import Base
from sqlalchemy.sql import func
import enum

class Resume(Base):
    __tablename__ = 'resumes'
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    name = Column(String, nullable=False)
    email = Column(String, nullable=False)
    phone = Column(String, nullable=True)
    linkedin = Column(String, nullable=True)
    github = Column(String, nullable=True)
    summary = Column(Text, nullable=True)
    technical_skills = Column(JSONB, nullable=True)
    soft_skills = Column(JSONB, nullable=True)
    programming_languages = Column(JSONB, nullable=True)
    languages = Column(JSONB, nullable=True)
    total_experience = Column(Float, nullable=True)
    embedding = Column(JSONB, nullable=True)

    experience = relationship('ResumeExperience', back_populates='resume', cascade='all, delete-orphan')
    education = relationship('ResumeEducation', back_populates='resume', cascade='all, delete-orphan')
    projects = relationship('ResumeProject', back_populates='resume', cascade='all, delete-orphan')
    certifications = relationship('ResumeCertification', back_populates='resume', cascade='all, delete-orphan')

class ResumeExperience(Base):
    __tablename__ = 'resume_experience'
    id = Column(Integer, primary_key=True, index=True)
    resume_id = Column(Integer, ForeignKey('resumes.id'))
    title = Column(String, nullable=False)
    summary = Column(Text, nullable=True)
    start_date = Column(String, nullable=True)
    end_date = Column(String, nullable=True)
    organization = Column(String, nullable=True)
    resume = relationship('Resume', back_populates='experience')

class ResumeEducation(Base):
    __tablename__ = 'resume_education'
    id = Column(Integer, primary_key=True, index=True)
    resume_id = Column(Integer, ForeignKey('resumes.id'))
    title = Column(String, nullable=False)
    start_date = Column(String, nullable=True)
    end_date = Column(String, nullable=True)
    organization = Column(String, nullable=True)
    grade = Column(String, nullable=True)
    percentage = Column(String, nullable=True)
    resume = relationship('Resume', back_populates='education')

class ResumeProject(Base):
    __tablename__ = 'resume_project'
    id = Column(Integer, primary_key=True, index=True)
    resume_id = Column(Integer, ForeignKey('resumes.id'))
    title = Column(String, nullable=False)
    summary = Column(Text, nullable=True)
    start_date = Column(String, nullable=True)
    end_date = Column(String, nullable=True)
    technologies = Column(JSONB, nullable=True)
    programming_languages = Column(JSONB, nullable=True)
    resume = relationship('Resume', back_populates='projects')

class ResumeCertification(Base):
    __tablename__ = 'resume_certification'
    id = Column(Integer, primary_key=True, index=True)
    resume_id = Column(Integer, ForeignKey('resumes.id'))
    title = Column(String, nullable=False)
    organization = Column(String, nullable=True)
    end_date = Column(String, nullable=True)
    resume = relationship('Resume', back_populates='certifications')

class ResumeFileStatus(str, enum.Enum):
    pending = "pending"
    processing = "processing"
    parsed = "parsed"
    failed = "failed"

class ResumeFile(Base):
    __tablename__ = 'resume_files'
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    file_path = Column(String, nullable=False)
    filename = Column(String, nullable=False)
    status = Column(SqlEnum(ResumeFileStatus), default=ResumeFileStatus.pending, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now()) 