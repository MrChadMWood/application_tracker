# app/schemas.py
from pydantic import BaseModel, ConfigDict
from datetime import date


# Resume Schemas
class ResumeBase(BaseModel):
    data: str

class ResumeCreate(ResumeBase):
    pass

class Resume(ResumeBase):
    id: int

# Posting Schemas
class PostingBase(BaseModel):
    platform: str
    company: str
    title: str
    salary: float | None = None
    description: str | None = None
    responsibilities: str
    qualifications: str
    remote: bool | None = None

class PostingCreate(PostingBase):
    pass

class Posting(PostingBase):
    id: int

# Application Schemas
class ApplicationBase(BaseModel):
    posting_id: int
    resume_id: int
    date_submitted: date

class ApplicationCreate(ApplicationBase):
    pass

class Application(ApplicationBase):
    id: int

# ResponseType Schemas
class ResponseTypeBase(BaseModel):
    name: str

class ResponseTypeCreate(ResponseTypeBase):
    pass

class ResponseType(ResponseTypeBase):
    id: int

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
