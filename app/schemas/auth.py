from pydantic import BaseModel, Field
from app.schemas.user import UserRead


class RegisterRequest(BaseModel):
    username: str = Field(min_length=1)


class LoginRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    token: str
    user: UserRead


class UserRegistered(BaseModel):
    token: str
    user: UserRead
    generated_password: str