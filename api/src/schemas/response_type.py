# app/schemas/response_type.py
from pydantic import BaseModel


class ResponseTypeBase(BaseModel):
    name: str

class Create(ResponseTypeBase):
    pass

class Read(ResponseTypeBase):
    id: int