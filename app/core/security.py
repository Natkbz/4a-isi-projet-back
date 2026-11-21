import secrets
from pwdlib import PasswordHash
from fastapi import HTTPException, status
from datetime import datetime, timedelta, timezone
import jwt
from jwt.exceptions import InvalidTokenError
from app.core.config import ACCESS_TOKEN_EXPIRE_MINUTES, ALGORITHM, SECRET_KEY
from typing import Optional


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