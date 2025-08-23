from fastapi import APIRouter, Depends, status, HTTPException, Path
from ..models import Todos
from ..database import SessionLocal
from sqlalchemy.orm import Session
from typing import Annotated, Optional
from pydantic import BaseModel, Field
from .auth import get_current_user

router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]

class TodoRequest(BaseModel):
    title: str = Field(..., min_length=3)
    description: str = Field(..., min_length=3, max_length=100)
    priority: int = Field(gt=0, lt=6)
    complete: bool

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "title": "Buy groceries",
                    "description": "Buy groceries",
                    "priority": 2,
                    "complete": False,
                }
            ]
        }
    }


class TodoUpdateRequest(BaseModel):
    title: Optional[str] = Field(None, min_length=3)
    description: Optional[str] = Field(None, min_length=3, max_length=100)
    priority: Optional[int] = Field(None, gt=0, lt=6)
    complete: Optional[bool] = None

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "title": "Updated title",
                    "description": "Updated description",
                    "priority": 3,
                    "complete": True,
                }
            ]
        }
    }


@router.get("/", status_code=status.HTTP_200_OK)
async def read_all(user: user_dependency, db: db_dependency):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not authenticated")
    return db.query(Todos).filter(Todos.owner_id == user.get("id")).all()


@router.get("/todo/{todo_id}", status_code=status.HTTP_200_OK)
async def read_todo(user: user_dependency, db: db_dependency, todo_id: int = Path(gt=0)):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not authenticated")
    todo_model = db.query(Todos).filter(Todos.id == todo_id, Todos.owner_id == user.get("id")).first()
    if todo_model is None:
        raise HTTPException(status_code=404, detail="Todo not found")
    return todo_model


@router.post("/todo", status_code=status.HTTP_201_CREATED)
async def create_todo(user: user_dependency, db: db_dependency, todo_request: TodoRequest):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not authenticated")
    todo_model = Todos(**todo_request.model_dump(), owner_id=user.get("id"))
    db.add(todo_model)
    db.commit()


@router.put("/todo/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def update_todo(
    user: user_dependency, db: db_dependency, todo_request: TodoUpdateRequest, todo_id: int = Path(gt=0)
    ):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not authenticated")
    todo_model = db.query(Todos).filter(Todos.id == todo_id, Todos.owner_id == user.get("id")).first()
    if todo_model is None:
        raise HTTPException(status_code=404, detail="todo not found")
    # Chỉ cập nhật các field có giá trị
    if todo_request.title is not None:
        todo_model.title = todo_request.title
    if todo_request.description is not None:
        todo_model.description = todo_request.description
    if todo_request.priority is not None:
        todo_model.priority = todo_request.priority
    if todo_request.complete is not None:
        todo_model.complete = todo_request.complete
    db.add(todo_model)
    db.commit()


@router.delete("/todo/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo(user: user_dependency, db: db_dependency, todo_id: int = Path(gt=0)):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not authenticated")
    todo_model = db.query(Todos).filter(Todos.id == todo_id, Todos.owner_id == user.get("id")).first()
    if todo_model is None:
        raise HTTPException(status_code=404, detail="Todo not found")
    db.query(Todos).filter(Todos.id == todo_id, Todos.owner_id == user.get("id")).delete()
    db.commit()
