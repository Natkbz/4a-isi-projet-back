from fastapi import APIRouter, Depends
from sqlmodel import Session

from app.core.security import get_current_user
from app.schemas.order import OrderRead
from db import crud
from db.database import get_session
from db.models import User
from app.services.order_service import build_order_read

router = APIRouter(tags=["Orders"])


@router.get("/orders", response_model=list[OrderRead])
def list_my_orders(current_user: User = Depends(get_current_user), session: Session = Depends(get_session)):
    if current_user.id is None:
        raise ValueError("Identifiant utilisateur manquant.")

    orders = crud.get_orders_by_user(session, current_user.id)
    to_return = []
    for order in orders:
        to_return.append(build_order_read(order))
    return to_return