from fastapi import APIRouter, Depends, HTTPException
from src.deps import get_db
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm
from src.models import User
from bcrypt import checkpw
from src.schemas import LoginOut, RefreshTokenRequest, TokenRefreshOut
from src.auth.auth_utils import (
    create_access_token,
    create_refresh_token,
    verify_refresh_token,
)

router = APIRouter()


@router.post("/login", response_model=LoginOut)
def login_user(
    form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)
):
    db_user = db.query(User).filter(User.username == form_data.username).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    if not checkpw(
        form_data.password.encode("utf-8"), db_user.password_hash.encode("utf-8")
    ):
        raise HTTPException(status_code=401, detail="Invalid password")

    access_token = create_access_token(data={"sub": str(db_user.id)})
    refresh_token = create_refresh_token(data={"sub": str(db_user.id)})
    return {
        "id": db_user.id,
        "username": db_user.username,
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }


@router.post("/refresh", response_model=TokenRefreshOut)
def refresh_token(request: RefreshTokenRequest, db: Session = Depends(get_db)):
    payload = verify_refresh_token(request.refresh_token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    user_id = payload.get("sub")
    user_db = db.query(User).filter(User.id == int(user_id)).first()

    if not user_db:
        raise HTTPException(status_code=404, detail="User not found")

    access_token = create_access_token(data={"sub": str(user_id)})
    refresh_token = create_refresh_token(data={"sub": str(user_id)})
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }
