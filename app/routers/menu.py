from fastapi import APIRouter, Depends
from sqlmodel import Session
from app.schemas.menu import MenuRead
from app.services.menu_service import build_menu_read
from db import crud
from db.database import get_session

router = APIRouter(tags=["Menus"])


@router.get("/menus", response_model=list[MenuRead])
def list_menus(session: Session = Depends(get_session)):
    menus = crud.get_all_menus(session)
    to_return =[]
    for menu in menus:
        to_return.append(build_menu_read(menu))
    return to_return