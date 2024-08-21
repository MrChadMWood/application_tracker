# src/models.py
from sqlalchemy import Column, Integer, String, Text, Boolean, ForeignKey, Date, JSON, Double
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Resume(Base):
    __tablename__ = "resume"

    id = Column(Integer, primary_key=True, index=True)
    data = Column(JSON, nullable=False)

class JobPosting(Base):
    __tablename__ = "posting"

    id = Column(Integer, primary_key=True, index=True)
    platform = Column(String, nullable=False)
    company = Column(String, nullable=False)
    title = Column(String, nullable=False)
    salary = Column(Double)
    description = Column(Text)
    responsibilities = Column(String)
    qualifications = Column(String)
    remote = Column(Boolean)

class JobApplication(Base):
    __tablename__ = "application"

    id = Column(Integer, primary_key=True, index=True)
    posting_id = Column(Integer, ForeignKey("posting.id"), nullable=False)
    resume_id = Column(Integer, ForeignKey("resume.id"), nullable=False)
    date_submitted = Column(Date, nullable=False)

    posting = relationship("JobPosting")
    resume = relationship("Resume")

class ResponseType(Base):
    __tablename__ = "response_type"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)

class Response(Base):
    __tablename__ = "response"

    id = Column(Integer, primary_key=True, index=True)
    application_id = Column(Integer, ForeignKey("application.id"), nullable=False)
    response_type_id = Column(Integer, ForeignKey("response_type.id"), nullable=False)
    date_received = Column(Date, nullable=False)
    data = Column(String)

    application = relationship("JobApplication")
    response_type = relationship("ResponseType")
