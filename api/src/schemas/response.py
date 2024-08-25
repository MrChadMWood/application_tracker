# app/schemas/response.py
from pydantic import BaseModel
from datetime import date


class ResponseBase(BaseModel):
    application_id: int
    response_type_id: int
    date_received: date
    data: str | None = None

class Create(ResponseBase):
    pass

class Read(ResponseBase):
    id: int
