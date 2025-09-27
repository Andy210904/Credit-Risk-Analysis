from fastapi import APIRouter, HTTPException, Depends, Response, Request
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session
from datetime import timedelta, datetime

from app.services.auth_service import auth_service
from app.models.database import User, get_session
from app.config import settings

router = APIRouter()

# Pydantic schemas
class RegisterRequest(BaseModel):
    username: str
    email: EmailStr
    password: str

class LoginRequest(BaseModel):
    username: str
    password: str

class UserOut(BaseModel):
    id: int
    username: str
    email: EmailStr
    is_active: bool

    class Config:
        from_attributes = True

COOKIE_NAME = "access_token"
COOKIE_MAX_AGE = 60 * 60 * 24  # 1 day for demo

# Dependency

def get_db():
    db = get_session()
    try:
        yield db
    finally:
        db.close()

@router.post('/register', response_model=UserOut)
def register(payload: RegisterRequest, db: Session = Depends(get_db)):
    # Uniqueness checks
    if auth_service.get_user_by_username(db, payload.username):
        raise HTTPException(status_code=400, detail='Username already taken')
    if auth_service.get_user_by_email(db, payload.email):
        raise HTTPException(status_code=400, detail='Email already registered')

    user = User(
        username=payload.username,
        email=payload.email,
        password_hash=auth_service.hash_password(payload.password)
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user.to_dict()

@router.post('/login', response_model=UserOut)
def login(payload: LoginRequest, response: Response, db: Session = Depends(get_db)):
    user = auth_service.authenticate_user(db, payload.username, payload.password)
    if not user:
        raise HTTPException(status_code=401, detail='Invalid credentials')

    token = auth_service.create_access_token({"sub": user.username}, expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES))

    # Set HttpOnly cookie
    response.set_cookie(
        key=COOKIE_NAME,
        value=token,
        httponly=True,
        max_age=COOKIE_MAX_AGE,
        secure=False,  # Set True behind HTTPS
        samesite='lax',
        path='/'
    )
    return user.to_dict()

@router.post('/logout')
def logout(response: Response):
    response.delete_cookie(COOKIE_NAME, path='/')
    return {"message": "Logged out"}

@router.get('/me', response_model=UserOut)
def me(request: Request, db: Session = Depends(get_db)):
    token = request.cookies.get(COOKIE_NAME)
    if not token:
        raise HTTPException(status_code=401, detail='Not authenticated')
    payload = auth_service.decode_token(token)
    username = payload.get('sub')
    if not username:
        raise HTTPException(status_code=401, detail='Invalid token payload')
    user = auth_service.get_user_by_username(db, username)
    if not user:
        raise HTTPException(status_code=404, detail='User not found')
    return user.to_dict()
