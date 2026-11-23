import secrets
from pwdlib import PasswordHash
from fastapi import HTTPException, status, Depends
from datetime import datetime, timedelta, timezone
import jwt
from jwt.exceptions import InvalidTokenError
from app.core.config import ACCESS_TOKEN_EXPIRE_MINUTES, ALGORITHM, SECRET_KEY
from typing import Optional
from db.models import User, UserRole
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from sqlmodel import Session
from db import crud
from db.database import get_session
from db.models import User, UserRole

#gestion des mots de passe
# Contexte de hachage Argon2
password_hasher = PasswordHash.recommended()

def generate_random_password(length: int = 12) -> str:
    """Génère un mot de passe aléatoire sécurisé"""
    return secrets.token_urlsafe(length)


def hash_password(plain_password: str) -> str:
    """hache un mot de passe"""
    return password_hasher.hash(plain_password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Vérifie le mot de passe comparé à son hash"""
    return password_hasher.verify(plain_password, hashed_password)


#Gestion du token

def create_access_token(user_id: int, expires_delta: Optional[timedelta] = None) -> str:
    """Crée un jeton JWT signé avec l'id du user"""
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    payload = {
        "sub": str(user_id),
        "exp": expire,
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def decode_access_token(token: str) -> int:
    """Décode un jeton JWT et return id user"""
    credentials_exception = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token invalide ou expiré", headers={"WWW-Authenticate": "Bearer"})
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id_str = payload.get("sub")
        if user_id_str is None:
            raise credentials_exception
        return int(user_id_str)
    except (InvalidTokenError, ValueError):
        raise credentials_exception
    
#gestion de la récupération de l'user ou de l'admin

# auto_error=False pour renvoyer 401 quand le header Authorization est absent
bearer_scheme = HTTPBearer(auto_error=False)    

def get_current_user(credentials: Optional[HTTPAuthorizationCredentials] = Depends(bearer_scheme),session: Session = Depends(get_session)) -> User:
    """Vérifie le token Bearer, charge l'utilisateur et contrôle qu'il n'est pas bloqué."""
    
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Token d'authentification manquant",headers={"WWW-Authenticate": "Bearer"})

    user_id = decode_access_token(credentials.credentials)

    # Récupération de l'user avec L'id en db 
    user = crud.get_user_by_id(session, user_id)

    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Utilisateur introuvable",headers={"WWW-Authenticate": "Bearer"})

    if user.is_blocked:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail="Votre compte a été bloqué")

    return user


def get_current_admin(current_user: User = Depends(get_current_user)) -> User:
    """Retourne l'user si il est bien un admin"""
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail="Droits administrateur requis")
    return current_user