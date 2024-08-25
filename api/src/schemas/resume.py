# app/schemas/resume.py
from pydantic import BaseModel


# Resume Schemas
class ResumeBase(BaseModel):
    data: str

class Create(ResumeBase):
    pass

class Read(ResumeBase):
    id: int
