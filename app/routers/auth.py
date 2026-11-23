from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session

from app.core.security import (generate_random_password, hash_password, verify_password, create_access_token)
from app.schemas.user import UserRegister, UserRegisterResponse, UserLogin, Token
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

@router.post("/login", response_model=Token, status_code=status.HTTP_200_OK)
def login(payload: UserLogin, session: Session = Depends(get_session)):
    user = crud.get_user_by_username(session, payload.username)

    if user is None or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Nom d'utilisateur ou mot de passe incorrect",
            headers={"WWW-Authenticate": "Bearer"})

    if user.is_blocked:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail="Votre compte a été bloqué par un admin")

    if user.id is None:
        raise ValueError("Identifiant utilisateur requis")
    
    access_token = create_access_token(user.id)
    return Token(access_token=access_token, token_type="bearer")