from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session

from app.core.security import (generate_random_password, hash_password)
from app.schemas.user import UserRegister, UserRegisterResponse
from db import crud
from db.database import get_session

router = APIRouter(tags=["Auth"])


@router.post("/register", response_model=UserRegisterResponse, status_code=status.HTTP_201_CREATED)
def register(payload: UserRegister, session: Session = Depends(get_session)):
    plain_password = generate_random_password()
    hashed = hash_password(plain_password)

    try:
        user = crud.create_user(session, username=payload.username, password_hash=hashed)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,detail="Ce nom d'utilisateur est déjà utilisé")

    if user.id is None:
        raise ValueError("L'utilisateur doit avoir un id après enregistrement")

    return UserRegisterResponse(id=user.id, username=user.username, role=user.role, is_blocked=user.is_blocked, created_at=user.created_at, password=plain_password)