from datetime import date

from pydantic import BaseModel, EmailStr


class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str


class UserOut(BaseModel):
    id: int
    username: str
    email: EmailStr

    class Config:
        from_attributes = True


class UserLogin(BaseModel):
    username: str
    password: str


class LoginOut(BaseModel):
    id: int
    username: str
    access_token: str
    refresh_token: str
    token_type: str


class RefreshTokenRequest(BaseModel):
    refresh_token: str


class TokenRefreshOut(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str


class StudentOut(BaseModel):
    id: int
    username: str

    class Config:
        from_attributes = True


class OTPRequest(BaseModel):
    email: EmailStr


class OTPVerify(BaseModel):
    email: EmailStr
    otp: str


class SubjectCreate(BaseModel):
    subject_name: str
    exam_date: date
    difficulty: str


class TopicCreate(BaseModel):
    topic_name: str
    priority_level: str = "medium"
    estimated_hours: int | None = None
    is_completed: bool = False


class TopicUpdate(BaseModel):
    topic_name: str | None = None
    priority_level: str | None = None
    estimated_hours: int | None = None
    is_completed: bool | None = None
