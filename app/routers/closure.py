from fastapi import APIRouter, Depends
from sqlmodel import Session

from app.schemas.closure import ClosureRead
from db import crud
from db.database import get_session

router = APIRouter(tags=["Closures"])


@router.get("/closures", response_model=list[ClosureRead])
def list_closures(session: Session = Depends(get_session)):
    return crud.get_all_closure_days(session)