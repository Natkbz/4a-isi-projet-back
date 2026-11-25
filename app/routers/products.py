from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session

from app.schemas.product import ProductRead,ProductCreate
from db import crud
from db.database import get_session
from db.models import User
from app.core.security import get_current_admin

router = APIRouter(tags=["Products"])


@router.get("/products", response_model=list[ProductRead])
def list_products(session: Session = Depends(get_session)):
    return crud.get_all_products(session)

@router.post("/products", response_model=ProductRead, status_code=status.HTTP_201_CREATED)
def create_product(payload: ProductCreate, admin: User = Depends(get_current_admin), session: Session = Depends(get_session)):
    try:
        product = crud.create_product(session, **payload.model_dump())
    except LookupError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    return product