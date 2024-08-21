# app/schemas.py
from pydantic import BaseModel
from datetime import date


# Resume Schemas
class ResumeBase(BaseModel):
    data: str

class ResumeCreate(ResumeBase):
    pass

class Resume(ResumeBase):
    id: int

    class Config:
        from_attributes = True

# JobPosting Schemas
class JobPostingBase(BaseModel):
    platform: str
    company: str
    title: str
    salary: float | None = None
    description: str | None = None
    responsibilities: str
    qualifications: str
    remote: bool | None = None

class JobPostingCreate(JobPostingBase):
    pass

class JobPosting(JobPostingBase):
    id: int

    class Config:
        from_attributes = True

# JobApplication Schemas
class JobApplicationBase(BaseModel):
    posting_id: int
    resume_id: int
    date_submitted: date

class JobApplicationCreate(JobApplicationBase):
    pass

class JobApplication(JobApplicationBase):
    id: int

    class Config:
        from_attributes = True

# ResponseType Schemas
class ResponseTypeBase(BaseModel):
    name: str

class ResponseTypeCreate(ResponseTypeBase):
    pass

class ResponseType(ResponseTypeBase):
    id: int

    class Config:
        from_attributes = True

# Response Schemas
class ResponseBase(BaseModel):
    application_id: int
    response_type_id: int
    date_received: date
    data: str | None = None

class ResponseCreate(ResponseBase):
    pass

class Response(ResponseBase):
    id: int

    class Config:
        from_attributes = True
