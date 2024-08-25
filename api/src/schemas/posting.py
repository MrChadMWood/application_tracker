# app/schemas/posting.py
from pydantic import BaseModel


class PostingBase(BaseModel):
    platform: str
    company: str
    title: str
    salary: float | None = None
    description: str | None = None
    responsibilities: str
    qualifications: str
    remote: bool | None = None

class Create(PostingBase):
    pass

class Read(PostingBase):
    id: int
