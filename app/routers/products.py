from fastapi import APIRouter, Depends
from sqlmodel import Session

from app.schemas.product import ProductRead
from db import crud
from db.database import get_session

router = APIRouter(tags=["Products"])


@router.get("/products", response_model=list[ProductRead])
def list_products(session: Session = Depends(get_session)):
    return crud.get_all_products(session)