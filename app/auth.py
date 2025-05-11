from fastapi import Depends, HTTPException, status
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
import os
from fastapi.security import OAuth2PasswordBearer
from app import models
from app.database import get_db
from sqlalchemy.orm import Session  # Use Session instead of AsyncSession
from sqlalchemy import select  # Sync query

# Replace this with a secret key stored in environment variable in production
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")

# --- Password hashing helpers --- #

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

# --- JWT Token generation --- #

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

# --- Get Current User --- #

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    print("Inside get current user")
    print("token: ", token)
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        print("Payload: ", payload)
        user_id: int = payload.get("sub")
        print(user_id)
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    result = db.execute(select(models.User).where(models.User.id == int(user_id)))  # Sync query
    user = result.scalar_one_or_none()  # Sync execution
    if user is None:
        raise credentials_exception
    print("CURRENT USER1: ",user)
    return user
