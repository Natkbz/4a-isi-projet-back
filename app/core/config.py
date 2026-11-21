import os

# Clé secrète pour signer les jetons JWT
SECRET_KEY: str = os.getenv("SECRET_KEY", "poleatheck-secret-key-tp-isi-numero-cinq")
ALGORITHM: str = "HS256"

# Durée de validité d'un jeton JWT (12 heures)
ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 10

# Longueur minimale exigée lors du changement de mot de passe
MIN_PASSWORD_LENGTH: int = 8