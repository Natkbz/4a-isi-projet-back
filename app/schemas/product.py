from typing import Optional
from pydantic import BaseModel, ConfigDict, Field


class ProductCreate(BaseModel):
    name: str = Field(min_length=1)
    description: Optional[str] = None
    price: float = Field(ge=0)
    stock: int = Field(ge=0)
    category_id: Optional[int] = None
    is_available: bool = True


class ProductUpdate(BaseModel):
    name: str = Field(min_length=1)
    description: Optional[str] = None
    price: float = Field(ge=0)
    stock: int = Field(ge=0)
    category_id: Optional[int] = None
    is_available: bool
    is_deleted: bool


class ProductRead(BaseModel):
    id: int
    category_id: Optional[int]
    name: str
    description: Optional[str]
    price: float
    stock: int
    is_available: bool
    is_deleted: bool

    model_config = ConfigDict(from_attributes=True)