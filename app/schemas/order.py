from datetime import date, datetime
from pydantic import BaseModel, ConfigDict, Field
from db.models import OrderStatus


class OrderProductCreate(BaseModel):
    product_id: int
    quantity: int = Field(ge=1)


class OrderMenuCreate(BaseModel):
    menu_id: int
    quantity: int = Field(ge=1)


class OrderCreate(BaseModel):
    pickup_date: date
    products: list[OrderProductCreate] = []
    menus: list[OrderMenuCreate] = []


class OrderStatusUpdate(BaseModel):
    status: OrderStatus


class OrderProductRead(BaseModel):
    id: int
    product_id: int
    product_name: str
    quantity: int
    unit_price: float

    model_config = ConfigDict(from_attributes=True)


class OrderMenuRead(BaseModel):
    id: int
    menu_id: int
    menu_name: str
    quantity: int
    unit_price: float

    model_config = ConfigDict(from_attributes=True)


class OrderRead(BaseModel):
    id: int
    user_id: int
    created_at: datetime
    pickup_date: date
    status: OrderStatus
    products: list[OrderProductRead]
    menus: list[OrderMenuRead]

    model_config = ConfigDict(from_attributes=True)