from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from src.deps import get_db
from src.models import User
from src.schemas import UserCreate, UserOut, OTPRequest, OTPVerify
from bcrypt import hashpw, gensalt
from src.routes.login import router as login_router
from src.routes.studentlog import route as student_login
from src.auth.otp import generate_otp, save_otp, verify_otp
from src.email_service import send_otp_email
from src.routes.subjects import router as subjects_router
from src.AI.generate_tableAI import router as table_gen

app = FastAPI()

app.include_router(table_gen)
app.include_router(login_router)
app.include_router(student_login, prefix="")
app.include_router(subjects_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def user():
    return {"hello": "world"}


@app.post("/users", response_model=UserOut)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    try:
        db_user = User(
            username=user.username,
            email=user.email,
            password_hash=hashpw(user.password.encode("utf-8"), gensalt(12)).decode(
                "utf-8"
            ),
        )

        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user

    except IntegrityError as e:
        db.rollback()

        if "username" in str(e.orig):
            raise HTTPException(400, "Username already exists")

        if "email" in str(e.orig):
            raise HTTPException(400, "Email already exists")

        raise HTTPException(400, "Duplicate entry")


@app.get("/users/{user_id}", response_model=UserOut)
def read_user(user_id: int, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.id == user_id).first()
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user


@app.post("/request-otp")
async def request_otp(otp_request: OTPRequest):
    otp = generate_otp()
    await save_otp(otp_request.email, otp)
    send_otp_email(otp_request.email, otp)
    return {"message": "OTP sent to email"}


@app.post("/verify-otp")
async def verify_otp_endpoint(otp_verify: OTPVerify):
    is_valid = await verify_otp(otp_verify.email, otp_verify.otp)
    if is_valid:
        return {"message": "OTP verified successfully"}
    else:
        raise HTTPException(status_code=400, detail="Invalid OTP")
