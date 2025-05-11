from datetime import date
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session  # Import Session for sync DB
from sqlalchemy import select  # Sync query
from .. import models, schemas, database, auth
from ..utils.notifications import check_and_notify_limit


router = APIRouter(
    prefix="/expenses",
    tags=["Expenses"]
)

# Dependency to get DB session
get_db = database.get_db


# Create new expense
@router.post("/", response_model=schemas.ExpenseRead)
def create_expense(expense: schemas.ExpenseCreate, db: Session = Depends(get_db),
                   current_user: models.User = Depends(auth.get_current_user)):
    
    new_expense = models.Expense(**expense.dict())
    db.add(new_expense)
    db.commit()
    db.refresh(new_expense)
    today = date.today()
    result = db.execute(
        select(models.Expense).where(
            models.Expense.owner_id == current_user.id,
            models.Expense.date == today
        )
    )
    expenses_today = result.scalars().all()

    # Call the notification checker
    check_and_notify_limit(current_user, expenses_today, current_user.daily_limit)

    return new_expense


# Get all expenses
@router.get("/", response_model=list[schemas.ExpenseRead])
def read_expenses(db: Session = Depends(get_db), 
                  current_user: models.User = Depends(auth.get_current_user)):
    print("INSIDE read expenses")
    result = db.execute(
        select(models.Expense).where(models.Expense.owner_id == current_user.id)
    )
    return result.scalars().all()


# Get one expense by ID
@router.get("/{expense_id}", response_model=schemas.ExpenseRead)
def read_expense(expense_id: int, db: Session = Depends(get_db),
                 current_user: models.User = Depends(auth.get_current_user)):
    
    print("#####", expense_id)
    result = db.execute(select(models.Expense).where(models.Expense.id == expense_id))
    expense = result.scalar_one_or_none()
    if not expense:
        raise HTTPException(status_code=404, detail="Expense not found")
    return expense


# Delete expense
@router.delete("/{expense_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_expense(expense_id: int, db: Session = Depends(get_db),
                   current_user: models.User = Depends(auth.get_current_user)):
    result = db.execute(select(models.Expense).where(models.Expense.id == expense_id))
    expense = result.scalar_one_or_none()
    if not expense:
        raise HTTPException(status_code=404, detail="Expense not found")
    db.delete(expense)
    db.commit()
    return


# Update expense
@router.put("/{expense_id}", response_model=schemas.ExpenseRead)
def update_expense(expense_id: int, updated_data: schemas.ExpenseCreate, db: Session = Depends(get_db),
                   current_user: models.User = Depends(auth.get_current_user)):
    result = db.execute(select(models.Expense).where(models.Expense.id == expense_id))
    expense = result.scalar_one_or_none()
    if not expense:
        raise HTTPException(status_code=404, detail="Expense not found")

    for key, value in updated_data.dict().items():
        setattr(expense, key, value)

    db.commit()
    db.refresh(expense)
    today = date.today()
    result = db.execute(
        select(models.Expense).where(
            models.Expense.owner_id == current_user.id,
            models.Expense.date == today
        )
    )
    expenses_today = result.scalars().all()
    # Call the notification checker
    print("CURRENT USER: ",current_user)
    check_and_notify_limit(current_user, expenses_today, current_user.daily_limit)

    return expense
