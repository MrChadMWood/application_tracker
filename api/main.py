# app/main.py
from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel
from pydantic_core import PydanticUndefined
from sqlalchemy.orm import Session
import re
from src.schemas import Resume
from src.schemas import ResumeCreate
from src.schemas import JobPosting
from src.schemas import JobPostingCreate
from src.schemas import JobApplication
from src.schemas import JobApplicationCreate
from src.schemas import ResponseType
from src.schemas import ResponseTypeCreate
from src.schemas import Response
from src.schemas import ResponseCreate
from src.crud import create_resume
from src.crud import get_resume
from src.crud import get_all_resumes
from src.crud import update_resume
from src.crud import delete_resume
from src.crud import create_posting
from src.crud import get_posting
from src.crud import get_all_postings
from src.crud import update_posting
from src.crud import delete_posting
from src.crud import create_application
from src.crud import get_application
from src.crud import get_all_applications
from src.crud import update_application
from src.crud import delete_application
from src.crud import create_response_type
from src.crud import get_response_type
from src.crud import get_all_response_types
from src.crud import update_response_type
from src.crud import delete_response_type
from src.crud import create_response
from src.crud import get_response
from src.crud import get_all_responses
from src.crud import update_response
from src.crud import delete_response
from src.dependancies import get_db
from src.settings import hot_reload

app = FastAPI()


def get_model_fields(model: BaseModel) -> dict[str, dict[str, object]]:
    fields = {}
    type_pattern = re.compile(r"<class '(.*)'>")
    for field_name, field_info in model.__fields__.items():
        field_data = {
            "type": type_pattern.sub(r'\1', str(field_info.annotation))
        }
        default = model.__fields__[field_name].default
        default_factory = model.__fields__[field_name].default_factory
        
        field_data["required"] = default == PydanticUndefined and default_factory is None
        
        if default is not PydanticUndefined:
            field_data["default"] = default if default is not None else "None"
        elif default_factory is not None:
            field_data["default_factory"] = default_factory.__name__
        
        fields[field_name] = field_data
    
    return fields

# Resume Endpoints
@app.post("/resumes/", response_model=Resume)
def create_resume_endpoint(resume: ResumeCreate, db: Session = Depends(get_db)):
    return create_resume(db=db, resume=resume)

@app.get("/resumes/", response_model=list[Resume])
def read_all_resumes_endpoint(db: Session = Depends(get_db)):
    resume = get_all_resumes(db=db)

    if resume is None:
        raise HTTPException(status_code=404, detail="Resume not found")
    return resume

@app.get("/resumes/{resume_id}", response_model=Resume)
def read_resume_endpoint(resume_id: int, db: Session = Depends(get_db)):
    resume = get_resume(db=db, resume_id=resume_id)

    if resume is None:
        raise HTTPException(status_code=404, detail="Resume not found")
    return resume

@app.get("/fields/{model}")
def read_fields_endpoint(model: str):
    models = {
        'response': Response,
        'application': JobApplication,
        'posting': JobPosting,
        'response_type': ResponseType,
        'resume': Resume
    }

    req_model = models.get(model)
    if req_model is None:
        raise HTTPException(status_code=404, detail="Fields not found")
    else:
        fields = get_model_fields(req_model)
        return fields

@app.put("/resumes/{resume_id}", response_model=Resume)
def update_resume_endpoint(resume_id: int, resume: ResumeCreate, db: Session = Depends(get_db)):
    updated_resume = update_resume(db=db, resume_id=resume_id, resume=resume)
    if updated_resume is None:
        raise HTTPException(status_code=404, detail="Resume not found")
    return updated_resume

@app.delete("/resumes/{resume_id}", response_model=Resume)
def delete_resume_endpoint(resume_id: int, db: Session = Depends(get_db)):
    deleted_resume = delete_resume(db=db, resume_id=resume_id)
    if deleted_resume is None:
        raise HTTPException(status_code=404, detail="Resume not found")
    return deleted_resume

# JobPosting Endpoints
@app.post("/postings/", response_model=JobPosting)
def create_posting_endpoint(posting: JobPostingCreate, db: Session = Depends(get_db)):
    return create_posting(db=db, posting=posting)

@app.get("/postings/", response_model=list[JobPosting])
def read_all_postings_endpoint(db: Session = Depends(get_db)):
    posting = get_all_postings(db=db)

    if posting is None:
        raise HTTPException(status_code=404, detail="JobPosting not found")
    return posting

@app.get("/postings/{posting_id}", response_model=JobPosting)
def read_posting_endpoint(posting_id: int, db: Session = Depends(get_db)):
    posting = get_posting(db=db, resume_id=posting_id)

    if posting is None:
        raise HTTPException(status_code=404, detail="JobPosting not found")
    return posting

@app.put("/postings/{posting_id}", response_model=JobPosting)
def update_posting_endpoint(posting_id: int, posting: JobPostingCreate, db: Session = Depends(get_db)):
    updated_posting = update_posting(db=db, posting_id=posting_id, posting=posting)
    if updated_posting is None:
        raise HTTPException(status_code=404, detail="JobPosting not found")
    return updated_posting

@app.delete("/postings/{posting_id}", response_model=JobPosting)
def delete_posting_endpoint(posting_id: int, db: Session = Depends(get_db)):
    deleted_posting = delete_posting(db=db, posting_id=posting_id)
    if deleted_posting is None:
        raise HTTPException(status_code=404, detail="JobPosting not found")
    return deleted_posting

# JobApplication Endpoints
@app.post("/applications/", response_model=JobApplication)
def create_application_endpoint(application: JobApplicationCreate, db: Session = Depends(get_db)):
    return create_application(db=db, application=application)

@app.get("/applications/", response_model=list[JobApplication])
def read_all_applications_endpoint(db: Session = Depends(get_db)):
    application = get_all_applications(db=db)

    if application is None:
        raise HTTPException(status_code=404, detail="JobApplication not found")
    return application

@app.get("/applications/{application_id}", response_model=JobApplication)
def read_application_endpoint(application_id: int, db: Session = Depends(get_db)):
    application = get_application(db=db, application_id=application_id)

    if application is None:
        raise HTTPException(status_code=404, detail="JobApplication not found")
    return application

@app.put("/applications/{application_id}", response_model=JobApplication)
def update_application_endpoint(application_id: int, application: JobApplicationCreate, db: Session = Depends(get_db)):
    updated_application = update_application(db=db, application_id=application_id, application=application)
    if updated_application is None:
        raise HTTPException(status_code=404, detail="JobApplication not found")
    return updated_application

@app.delete("/applications/{application_id}", response_model=JobApplication)
def delete_application_endpoint(application_id: int, db: Session = Depends(get_db)):
    deleted_application = delete_application(db=db, application_id=application_id)
    if deleted_application is None:
        raise HTTPException(status_code=404, detail="JobApplication not found")
    return deleted_application

# ResponseType Endpoints
@app.post("/response_types/", response_model=ResponseType)
def create_response_type_endpoint(response_type: ResponseTypeCreate, db: Session = Depends(get_db)):
    return create_response_type(db=db, response_type=response_type)

@app.get("/response_types/", response_model=list[ResponseType])
def read_all_response_types_endpoint(db: Session = Depends(get_db)):
    response_type = get_all_response_types(db=db)

    if response_type is None:
        raise HTTPException(status_code=404, detail="ResponseType not found")
    return response_type

@app.get("/response_types/{response_type_id}", response_model=ResponseType)
def read_response_type_endpoint(response_type_id: int, db: Session = Depends(get_db)):
    response_type = get_response_type(db=db, response_type_id=response_type_id)

    if response_type is None:
        raise HTTPException(status_code=404, detail="ResponseType not found")
    return response_type

@app.put("/response_types/{response_type_id}", response_model=ResponseType)
def update_response_type_endpoint(response_type_id: int, response_type: ResponseTypeCreate, db: Session = Depends(get_db)):
    updated_response_type = update_response_type(db=db, response_type_id=response_type_id, response_type=response_type)
    if updated_response_type is None:
        raise HTTPException(status_code=404, detail="ResponseType not found")
    return updated_response_type

@app.delete("/response_types/{response_type_id}", response_model=ResponseType)
def delete_response_type_endpoint(response_type_id: int, db: Session = Depends(get_db)):
    deleted_response_type = delete_response_type(db=db, response_type_id=response_type_id)
    if deleted_response_type is None:
        raise HTTPException(status_code=404, detail="ResponseType not found")
    return deleted_response_type

# Response Endpoints
@app.post("/responses/", response_model=Response)
def create_response_endpoint(response: ResponseCreate, db: Session = Depends(get_db)):
    return create_response(db=db, response=response)

@app.get("/responses/", response_model=list[Response])
def read_all_responses_endpoint(db: Session = Depends(get_db)):
    response = get_all_responses(db=db)

    if response is None:
        raise HTTPException(status_code=404, detail="Response not found")
    return response

@app.get("/responses/{response_id}", response_model=Response)
def read_response_endpoint(response_id: int, db: Session = Depends(get_db)):
    response = get_response(db=db, response_id=response_id)

    if response is None:
        raise HTTPException(status_code=404, detail="Response not found")
    return response

@app.put("/responses/{response_id}", response_model=Response)
def update_response_endpoint(response_id: int, response: ResponseCreate, db: Session = Depends(get_db)):
    updated_response = update_response(db=db, response_id=response_id, response=response)
    if updated_response is None:
        raise HTTPException(status_code=404, detail="Response not found")
    return updated_response

@app.delete("/responses/{response_id}", response_model=Response)
def delete_response_endpoint(response_id: int, db: Session = Depends(get_db)):
    deleted_response = delete_response(db=db, response_id=response_id)
    if deleted_response is None:
        raise HTTPException(status_code=404, detail="Response not found")
    return deleted_response

if __name__ == "__main__":
    import uvicorn
    uvicorn.run('main:app', host="0.0.0.0", port=8000, reload=hot_reload)
