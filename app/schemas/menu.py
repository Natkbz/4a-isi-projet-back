from datetime import date, datetime, timezone
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field


class MenuProductItem(BaseModel):
    product_id: int
    quantity: int = Field(ge=1)

    model_config = ConfigDict(from_attributes=True)


class MenuCreate(BaseModel):
    name: str = Field(min_length=1)
    description: Optional[str] = None
    price: float = Field(ge=0)
    start_date: date = Field(default_factory=lambda: datetime.now(timezone.utc).date())
    end_date: Optional[date] = None
    is_available: bool = True
    products: list[MenuProductItem]


class MenuUpdate(BaseModel):
    name: str = Field(min_length=1)
    description: Optional[str] = None
    price: float = Field(ge=0)
    start_date: date
    end_date: Optional[date] = None
    is_available: bool
    is_deleted: bool
    products: list[MenuProductItem]


class MenuRead(BaseModel):
    id: int
    name: str
    description: Optional[str]
    price: float
    start_date: date
    end_date: Optional[date]
    is_available: bool
    is_deleted: bool
    available_stock: int
    products: list[MenuProductItem]

    model_config = ConfigDict(from_attributes=True)