import secrets
from pwdlib import PasswordHash

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