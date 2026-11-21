from datetime import date
from typing import Optional
from pydantic import BaseModel, ConfigDict


class ClosureCreate(BaseModel):
    closure_date: date
    reason: Optional[str] = None


class ClosureRead(BaseModel):
    id: int
    closure_date: date
    reason: Optional[str]

    model_config = ConfigDict(from_attributes=True)