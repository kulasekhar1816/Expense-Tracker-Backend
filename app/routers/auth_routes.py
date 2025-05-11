from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import select
from .. import models, schemas, database, auth

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)

# Dependency to get DB session
get_db = database.get_db

# --- Register --- #
@router.post("/register", response_model=schemas.UserBase)
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    # Check if user already exists
    result = db.execute(select(models.User).where(models.User.username == user.username))
    existing_user = result.scalars().first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    
    result = db.execute(select(models.User).where(models.User.email == user.email))
    existing_email = result.scalars().first()
    if existing_email:
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed_password = auth.hash_password(user.password)
    db_user = models.User(
        username=user.username,
        email=user.email,
        hashed_password=hashed_password
    )

    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

# --- Login --- #
@router.post("/login", response_model=schemas.Token)
def login(form_data: schemas.UserLogin, db: Session = Depends(get_db)):
    result = db.execute(select(models.User).where(models.User.username == form_data.username))
    user = result.scalars().first()

    if not user or not auth.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid username or password")

    user_id = user.id
    access_token = auth.create_access_token(data={"sub": str(user_id)})
    return {"access_token": access_token, "token_type": "bearer", "user_id": user_id}
