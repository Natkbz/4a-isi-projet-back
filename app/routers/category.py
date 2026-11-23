from fastapi import APIRouter, Depends
from sqlmodel import Session

from app.schemas.category import CategoryRead
from db import crud
from db.database import get_session

router = APIRouter(tags=["Categories"])


@router.get("/categories", response_model=list[CategoryRead])
def list_categories(session: Session = Depends(get_session)):
    return crud.get_all_categories(session)