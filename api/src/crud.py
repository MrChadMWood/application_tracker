# app/crud.py
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import NoResultFound
import src.schemas as schema
import src.models as model


class CRUDBase:
    def __init__(self, _model):
        self.model = _model

    def create(self, db: Session | AsyncSession, obj_in):
        db_obj = self.model(**obj_in.dict())
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def read(self, db: Session | AsyncSession, obj_id: int):
        try:
            return db.query(self.model).filter(self.model.id == obj_id).one()
        except NoResultFound:
            return None

    def read_all(self, db: Session | AsyncSession):
        return db.query(self.model).all()

    def update(self, db: Session | AsyncSession, obj_id: int, obj_in):
        db_obj = db.query(self.model).filter(self.model.id == obj_id).one()
        if db_obj:
            for key, value in obj_in.dict().items():
                setattr(db_obj, key, value)
            db.commit()
            db.refresh(db_obj)
        return db_obj

    def delete(self, db: Session | AsyncSession, obj_id: int):
        db_obj = db.query(self.model).filter(self.model.id == obj_id).one()
        if db_obj:
            db.delete(db_obj)
            db.commit()
        return db_obj


resume = CRUDBase(model.Resume)
posting = CRUDBase(model.JobPosting)
application = CRUDBase(model.JobApplication)
response_type = CRUDBase(model.ResponseType)
response = CRUDBase(model.Response)
