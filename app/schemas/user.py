from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field
from db.models import UserRole


class UserRead(BaseModel):
    id: int
    username: str
    role: UserRole
    is_blocked: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class PasswordUpdate(BaseModel):
    old_password: str = Field(..., min_length=1)
    new_password: str = Field(..., min_length=1)


class UserBlockUpdate(BaseModel):
    is_blocked: bool