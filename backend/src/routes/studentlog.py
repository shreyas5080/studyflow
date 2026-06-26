from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from src.deps import get_db
from sqlalchemy.orm import Session
from src.schemas import StudentOut
from src.models import User
from src.auth.auth_utils import verify_token

route = APIRouter()

Oauth = OAuth2PasswordBearer(tokenUrl="/login")


@route.get("/student/{user_id}", response_model=StudentOut)
def student_dash(
    user_id: int, token: str = Depends(Oauth), db: Session = Depends(get_db)
):

    data = verify_token(token)

    if not data:
        raise HTTPException(status_code=401, detail="invalid token")

    if int(data["sub"]) != user_id:
        raise HTTPException(status_code=403, detail="Not allowed")

    db_user = db.query(User).filter(User.id == user_id).first()

    if not db_user:
        raise HTTPException(status_code=404, detail="user not found")

    return db_user
