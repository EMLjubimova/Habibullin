from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app import crud, schemas, auth, models  # ← ДОБАВИЛИ models
from app.database import get_db

router = APIRouter(prefix="/items", tags=["items"])


@router.post("/", response_model=schemas.ItemResponse)
def create_item(
        item: schemas.ItemCreate,
        db: Session = Depends(get_db),
        current_user=Depends(auth.get_current_user)
):
    """
    Создать новый товар (только для авторизованных пользователей)
    """
    return crud.create_item(db=db, item=item, owner_id=current_user.id)


@router.get("/", response_model=List[schemas.ItemResponse])
def read_items(
        skip: int = 0,
        limit: int = 100,
        db: Session = Depends(get_db),
        current_user=Depends(auth.get_current_user)
):
    """
    Получить список всех товаров (только для авторизованных пользователей)
    """
    items = crud.get_items(db, skip=skip, limit=limit)
    return items


@router.get("/{item_id}", response_model=schemas.ItemResponse)
def read_item(
        item_id: int,
        db: Session = Depends(get_db),
        current_user=Depends(auth.get_current_user)
):
    """
    Получить информацию о конкретном товаре по ID
    """
    item = db.query(models.Item).filter(models.Item.id == item_id).first()  # ← ИСПРАВЛЕНО
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return item


@router.put("/{item_id}", response_model=schemas.ItemResponse)
def update_item(
        item_id: int,
        item_update: schemas.ItemCreate,
        db: Session = Depends(get_db),
        current_user=Depends(auth.get_current_user)
):
    """
    Обновить товар (только владелец)
    """
    item = db.query(models.Item).filter(  # ← ИСПРАВЛЕНО
        models.Item.id == item_id,  # ← ИСПРАВЛЕНО
        models.Item.owner_id == current_user.id  # ← ИСПРАВЛЕНО
    ).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found or not yours")

    item.name = item_update.name
    item.description = item_update.description
    item.price = item_update.price
    db.commit()
    db.refresh(item)
    return item


@router.delete("/{item_id}")
def delete_item(
        item_id: int,
        db: Session = Depends(get_db),
        current_user=Depends(auth.get_current_user)
):
    """
    Удалить товар (только владелец)
    """
    success = crud.delete_item(db, item_id, current_user.id)
    if not success:
        raise HTTPException(status_code=404, detail="Item not found or not yours")
    return {"message": "Item deleted successfully"}