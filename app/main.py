from fastapi import FastAPI, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1.api import api_router
from app.core.config import settings
from app.core.database import engine, Base, SessionLocal
from app.services.resume_service import process_pending_resumes
import threading
import time

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    debug=settings.DEBUG
)

# Set up CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(api_router, prefix="/api/v1")

def resume_processing_worker():
    while True:
        db = SessionLocal()
        try:
            process_pending_resumes(db)
        finally:
            db.close()
        time.sleep(10)  # Check every 10 seconds

@app.on_event("startup")
def start_resume_processing_worker():
    thread = threading.Thread(target=resume_processing_worker, daemon=True)
    thread.start()

@app.get("/")
def root():
    return {"message": f"Welcome to {settings.PROJECT_NAME}"}


@app.get("/health")
def health_check():
    return {"status": "healthy"}