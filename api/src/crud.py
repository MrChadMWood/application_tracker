# app/crud.py
from sqlalchemy.orm import Session
from src.models import Resume, JobPosting, JobApplication, ResponseType, Response
from src.schemas import ResumeCreate, JobPostingCreate, JobApplicationCreate, ResponseTypeCreate, ResponseCreate

# Resume CRUD
def create_resume(db: Session, resume: ResumeCreate):
    db_resume = Resume(**resume.dict())
    db.add(db_resume)
    db.commit()
    db.refresh(db_resume)
    return db_resume

def get_resume(db: Session, resume_id: int):
    return db.query(Resume).filter(Resume.id == resume_id).one()

def get_all_resumes(db: Session):
    return db.query(Resume).all()

def update_resume(db: Session, resume_id: int, resume: ResumeCreate):
    db_resume = db.query(Resume).filter(Resume.id == resume_id).one()
    if db_resume:
        for key, value in resume.dict().items():
            setattr(db_resume, key, value)
        db.commit()
        db.refresh(db_resume)
    return db_resume

def delete_resume(db: Session, resume_id: int):
    db_resume = db.query(Resume).filter(Resume.id == resume_id).one()
    if db_resume:
        db.delete(db_resume)
        db.commit()
    return db_resume

# JobPosting CRUD
def create_posting(db: Session, posting: JobPostingCreate):
    db_posting = JobPosting(**posting.dict())
    db.add(db_posting)
    db.commit()
    db.refresh(db_posting)
    return db_posting

def get_posting(db: Session, posting_id: int):
    return db.query(JobPosting).filter(JobPosting.id == posting_id).one()

def get_all_postings(db: Session):
    return db.query(JobPosting).all()

def update_posting(db: Session, posting_id: int, posting: JobPostingCreate):
    db_posting = db.query(JobPosting).filter(JobPosting.id == posting_id).one()
    if db_posting:
        for key, value in posting.dict().items():
            setattr(db_posting, key, value)
        db.commit()
        db.refresh(db_posting)
    return db_posting

def delete_posting(db: Session, posting_id: int):
    db_posting = db.query(JobPosting).filter(JobPosting.id == posting_id).one()
    if db_posting:
        db.delete(db_posting)
        db.commit()
    return db_posting

# JobApplication CRUD
def create_application(db: Session, application: JobApplicationCreate):
    db_application = JobApplication(**application.dict())
    db.add(db_application)
    db.commit()
    db.refresh(db_application)
    return db_application

def get_application(db: Session, application_id: int):
    return db.query(JobApplication).filter(JobApplication.id == application_id).one()

def get_all_applications(db: Session):
    return db.query(JobApplication).all()

def update_application(db: Session, application_id: int, application: JobApplicationCreate):
    db_application = db.query(JobApplication).filter(JobApplication.id == application_id).one()
    if db_application:
        for key, value in application.dict().items():
            setattr(db_application, key, value)
        db.commit()
        db.refresh(db_application)
    return db_application

def delete_application(db: Session, application_id: int):
    db_application = db.query(JobApplication).filter(JobApplication.id == application_id).one()
    if db_application:
        db.delete(db_application)
        db.commit()
    return db_application

# ResponseType CRUD
def create_response_type(db: Session, response_type: ResponseTypeCreate):
    db_response_type = ResponseType(**response_type.dict())
    db.add(db_response_type)
    db.commit()
    db.refresh(db_response_type)
    return db_response_type

def get_response_type(db: Session, response_type_id: int):
    return db.query(ResponseType).filter(ResponseType.id == response_type_id).one()

def get_all_response_types(db: Session):
    return db.query(ResponseType).all()

def update_response_type(db: Session, response_type_id: int, response_type: ResponseTypeCreate):
    db_response_type = db.query(ResponseType).filter(ResponseType.id == response_type_id).one()
    if db_response_type:
        for key, value in response_type.dict().items():
            setattr(db_response_type, key, value)
        db.commit()
        db.refresh(db_response_type)
    return db_response_type

def delete_response_type(db: Session, response_type_id: int):
    db_response_type = db.query(ResponseType).filter(ResponseType.id == response_type_id).one()
    if db_response_type:
        db.delete(db_response_type)
        db.commit()
    return db_response_type

# Response CRUD
def create_response(db: Session, response: ResponseCreate):
    db_response = Response(**response.dict())
    db.add(db_response)
    db.commit()
    db.refresh(db_response)
    return db_response

def get_response(db: Session, response_id: int):
    return db.query(Response).filter(Response.id == response_id).one()

def get_all_responses(db: Session):
    return db.query(Response).all()

def update_response(db: Session, response_id: int, response: ResponseCreate):
    db_response = db.query(Response).filter(Response.id == response_id).one()
    if db_response:
        for key, value in response.dict().items():
            setattr(db_response, key, value)
        db.commit()
        db.refresh(db_response)
    return db_response

def delete_response(db: Session, response_id: int):
    db_response = db.query(Response).filter(Response.id == response_id).one()
    if db_response:
        db.delete(db_response)
        db.commit()
    return db_response
