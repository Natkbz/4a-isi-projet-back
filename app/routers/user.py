from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session

from app.core.security import get_current_user, hash_password, verify_password
from app.schemas.user import PasswordUpdate, UserRead
from db.database import get_session
from db.models import User

router = APIRouter(tags=["Users"])

@router.patch("/users/password", status_code=status.HTTP_204_NO_CONTENT)
def update_own_password(payload: PasswordUpdate, current_user: User = Depends(get_current_user), session: Session = Depends(get_session)):
    if not verify_password(payload.old_password, current_user.password_hash):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Mot de passe actuel incorrect")

    current_user.password_hash = hash_password(payload.new_password)
    session.add(current_user)
    session.commit()
    return None

@router.get("/users/me", response_model=UserRead)
def read_current_user(current_user: User = Depends(get_current_user)):
    return current_user