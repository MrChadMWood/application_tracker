# app/schemas/application.py
from pydantic import BaseModel
from datetime import date


class ApplicationBase(BaseModel):
    posting_id: int
    resume_id: int
    date_submitted: date

class Create(ApplicationBase):
    pass

class Read(ApplicationBase):
    id: int
