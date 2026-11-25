from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session

from app.core.security import (create_access_token, generate_random_password, hash_password, verify_password)
from app.schemas.auth import (LoginRequest, RegisterRequest, TokenResponse,UserRegistered)
from app.schemas.user import UserRead
from db import crud
from db.database import get_session

router = APIRouter(tags=["Auth"])


@router.post("/register", response_model=UserRegistered, status_code=status.HTTP_201_CREATED)
def register(payload: RegisterRequest, session: Session = Depends(get_session)):
    plain_password = generate_random_password()
    hashed = hash_password(plain_password)

    try:
        user = crud.create_user(session, username=payload.username, password_hash=hashed)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Ce nom d'utilisateur est déjà utilisé")

    if user.id is None:
        raise ValueError("L'utilisateur doit avoir un id après enregistrement")

    token = create_access_token(user.id)

    return UserRegistered(token=token,user=UserRead.model_validate(user),generated_password=plain_password)


@router.post("/login", response_model=TokenResponse, status_code=status.HTTP_200_OK)
def login(payload: LoginRequest, session: Session = Depends(get_session)):
    user = crud.get_user_by_username(session, payload.username)

    if user is None or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Nom d'utilisateur ou mot de passe incorrect", headers={"WWW-Authenticate": "Bearer"})

    if user.is_blocked:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail="Votre compte a été bloqué par un admin")

    if user.id is None:
        raise ValueError("Identifiant utilisateur requis")

    access_token = create_access_token(user.id)
    return TokenResponse(token=access_token,user=UserRead.model_validate(user))