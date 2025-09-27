from datetime import datetime, timedelta
from typing import Optional
from jose import jwt, JWTError
from passlib.context import CryptContext
from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.config import settings
from app.models.database import User, get_session

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer(auto_error=False)

class AuthService:
    def __init__(self):
        self.secret_key = settings.SECRET_KEY
        self.algorithm = settings.ALGORITHM
        self.access_token_expire_minutes = settings.ACCESS_TOKEN_EXPIRE_MINUTES

    # Password hashing
    def hash_password(self, password: str) -> str:
        return pwd_context.hash(password)

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        return pwd_context.verify(plain_password, hashed_password)

    # JWT creation
    def create_access_token(self, data: dict, expires_delta: Optional[timedelta] = None) -> str:
        to_encode = data.copy()
        expire = datetime.utcnow() + (expires_delta or timedelta(minutes=self.access_token_expire_minutes))
        to_encode.update({"exp": expire, "iat": datetime.utcnow()})
        return jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)

    def decode_token(self, token: str) -> dict:
        try:
            return jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
        except JWTError as e:
            raise HTTPException(status_code=401, detail=f"Invalid token: {e}")

    def get_user_by_username(self, session: Session, username: str) -> Optional[User]:
        return session.query(User).filter(User.username == username).first()

    def get_user_by_email(self, session: Session, email: str) -> Optional[User]:
        return session.query(User).filter(User.email == email).first()

    def authenticate_user(self, session: Session, username: str, password: str) -> Optional[User]:
        user = self.get_user_by_username(session, username)
        if not user:
            return None
        if not self.verify_password(password, user.password_hash):
            return None
        return user

    def get_session(self):
        return get_session()

auth_service = AuthService()

# Dependency to get current user from bearer token if we later use Authorization header
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    if not credentials:
        raise HTTPException(status_code=401, detail="Not authenticated")
    token = credentials.credentials
    payload = auth_service.decode_token(token)
    username: str = payload.get("sub")
    if username is None:
        raise HTTPException(status_code=401, detail="Token missing subject")
    session = auth_service.get_session()
    try:
        user = auth_service.get_user_by_username(session, username)
        if not user:
            raise HTTPException(status_code=401, detail="User not found")
        return user
    finally:
        session.close()
