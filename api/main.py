# app/main.py
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
import src.schemas as schema
import src.crud as crud
from src.crud import CRUDBase
from src.dependancies import get_db
from src.settings import hot_reload
from typing import Type

app = FastAPI()


# Create crud endpoints dynamically
def generate_crud_routes(
    app: FastAPI,
    model_name: str,
    schema: Type[schema._proto.SchemaProtocol],
    crud_op: Type[CRUDBase]
):
    @app.post(f"/{model_name}/")
    def create_endpoint(item: schema.Create, db: Session = Depends(get_db)) -> schema.Read:
        return crud_op.create(db=db, obj_in=item)

    @app.get(f"/{model_name}/")
    def read_all_endpoint(db: Session = Depends(get_db)) -> list[schema.Read]:
        return crud_op.read_all(db=db)

    @app.get(f"/{model_name}/{{item_id}}")
    def read_endpoint(item_id: int, db: Session = Depends(get_db)) -> schema.Read:
        item = crud_op.read(db=db, obj_id=item_id)
        if item is None:
            raise HTTPException(status_code=404, detail=f"{model_name.capitalize()} not found")
        return item

    @app.put(f"/{model_name}/{{item_id}}")
    def update_endpoint(item_id: int, item: schema.Create, db: Session = Depends(get_db)) -> schema.Read:
        updated_item = crud_op.update(db=db, obj_id=item_id, obj_in=item)
        if updated_item is None:
            raise HTTPException(status_code=404, detail=f"{model_name.capitalize()} not found")
        return updated_item

    @app.delete(f"/{model_name}/{{item_id}}")
    def delete_endpoint(item_id: int, db: Session = Depends(get_db)) -> schema.Read:
        deleted_item = crud_op.delete(db=db, obj_id=item_id)
        if deleted_item is None:
            raise HTTPException(status_code=404, detail=f"{model_name.capitalize()} not found")
        return deleted_item

# Generate CRUD routes for each model
generate_crud_routes(app, "resumes", schema.resume, crud.resume)
generate_crud_routes(app, "postings", schema.posting, crud.posting)
generate_crud_routes(app, "applications", schema.application, crud.application)
generate_crud_routes(app, "response_types", schema.response_type, crud.response_type)
generate_crud_routes(app, "responses", schema.response, crud.response)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run('main:app', host="0.0.0.0", port=8000, reload=hot_reload)
