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