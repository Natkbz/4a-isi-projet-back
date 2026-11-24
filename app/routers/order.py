from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlmodel import Session

from app.core.security import get_current_user, get_current_admin
from app.schemas.order import OrderRead, OrderCreate, OrderStatus
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

@router.post("/orders", response_model=OrderRead, status_code=status.HTTP_201_CREATED)
def create_order(payload: OrderCreate, current_user: User = Depends(get_current_user), session: Session = Depends(get_session)):
    if current_user.id is None:
        raise ValueError("Identifiant utilisateur manquant.")

    product_items = []
    if payload.products is not None:
        for item in payload.products:
            product_items.append((item.product_id, item.quantity))

    menu_items = []
    if payload.menus is not None:
        for item in payload.menus:
            menu_items.append((item.menu_id, item.quantity))

    try:
        order = crud.create_order(session=session, user_id=current_user.id, pickup_date=payload.pickup_date, product_items=product_items, menu_items=menu_items)
    
    except LookupError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    return build_order_read(order)

@router.get("/admin/orders", response_model=list[OrderRead])
def list_all_orders(user_id: int | None = None, order_status: OrderStatus | None = Query(default=None, alias="status"),
    admin: User = Depends(get_current_admin),session: Session = Depends(get_session)):
    
    orders = crud.get_all_orders(session)

    to_return = []
    for order in orders:
        if user_id is not None and order.user_id != user_id:
            continue
        if order_status is not None and order.status != order_status:
            continue
        to_return.append(build_order_read(order))

    return to_return