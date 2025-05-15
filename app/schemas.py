from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime

# ----------------------------
# User Schemas
# ----------------------------

class UserBase(BaseModel):
    username:str

class UserCreate(UserBase):
    email: EmailStr
    password: str

class UserLogin(UserBase):
    password: str

class DailyLimitSchema(BaseModel):
    daily_limit: int

class UserRead(UserBase):
    id: int

    class Config:
        from_attributes = True  # This tells Pydantic to use SQLAlchemy attributes


# ----------------------------
# Expense Schemas
# ----------------------------

class ExpenseBase(BaseModel):
    title: str
    amount: float = Field(gt=0, description='Amount must be greater than 0')
    category: Optional[str] = None

class ExpenseCreate(ExpenseBase):
    owner_id: int  # Same fields as ExpenseBase; used for POST input

class ExpenseRead(ExpenseBase):
    id: int
    date: datetime
    owner_id: int

    class Config:
        from_attributes = True

# --- Token schemas --- #
class Token(BaseModel):
    access_token: str
    token_type: str
    user_id: int
    daily_limit: int

class TokenData(BaseModel):
    username: str | None = None
