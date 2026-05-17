from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app import crud, schemas, auth
from app.database import get_db

router = APIRouter(prefix="/users", tags=["users"])


@router.post("/", response_model=schemas.UserResponse)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    """
    Регистрация нового пользователя
    """
    # Проверяем, существует ли пользователь с таким username
    db_user = crud.get_user_by_username(db, username=user.username)
    if db_user:
        raise HTTPException(
            status_code=400,
            detail="Username already registered"
        )

    # Проверяем, существует ли пользователь с таким email
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )

    # Создаем нового пользователя
    return crud.create_user(db=db, user=user)


@router.get("/", response_model=List[schemas.UserResponse])
def read_users(
        skip: int = 0,
        limit: int = 100,
        db: Session = Depends(get_db),
        current_user=Depends(auth.get_current_user)
):
    """
    Получить список всех пользователей (только для авторизованных)
    """
    users = db.query(crud.models.User).offset(skip).limit(limit).all()
    return users


@router.get("/me", response_model=schemas.UserResponse)
def read_users_me(current_user=Depends(auth.get_current_user)):
    """
    Получить информацию о текущем авторизованном пользователе
    """
    return current_user


@router.get("/{user_id}", response_model=schemas.UserResponse)
def read_user_by_id(
        user_id: int,
        db: Session = Depends(get_db),
        current_user=Depends(auth.get_current_user)
):
    """
    Получить информацию о пользователе по ID (только для авторизованных)
    """
    user = crud.get_user(db, user_id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.put("/me", response_model=schemas.UserResponse)
def update_user_me(
        user_update: schemas.UserCreate,
        db: Session = Depends(get_db),
        current_user=Depends(auth.get_current_user)
):
    """
    Обновить информацию о себе
    """
    # Проверяем, не занят ли новый username
    if user_update.username != current_user.username:
        existing = crud.get_user_by_username(db, user_update.username)
        if existing:
            raise HTTPException(status_code=400, detail="Username already taken")

    # Обновляем данные
    current_user.username = user_update.username
    current_user.email = user_update.email
    if user_update.password:
        current_user.hashed_password = auth.get_password_hash(user_update.password)

    db.commit()
    db.refresh(current_user)
    return current_user


@router.delete("/me")
def delete_user_me(
        db: Session = Depends(get_db),
        current_user=Depends(auth.get_current_user)
):
    """
    Удалить свой аккаунт
    """
    db.delete(current_user)
    db.commit()
    return {"message": "User deleted successfully"}