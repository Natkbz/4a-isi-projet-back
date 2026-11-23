from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field
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
    
class UserRegister(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)


class UserRegisterResponse(UserRead):
    password: str


class UserLogin(BaseModel):
    username: str = Field(..., min_length=1)
    password: str = Field(..., min_length=1)


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"