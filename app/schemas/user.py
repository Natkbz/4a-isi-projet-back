from datetime import datetime
from pydantic import BaseModel, ConfigDict
from db.models import UserRole


class UserRead(BaseModel):
    id: int
    username: str
    role: UserRole
    is_blocked: bool
    created_at: datetime

    #permet transformer des objets python
    model_config = ConfigDict(from_attributes=True)


class PasswordUpdate(BaseModel):
    old_password: str
    new_password: str


class UserBlockUpdate(BaseModel):
    is_blocked: bool