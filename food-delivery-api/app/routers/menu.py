import uuid
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload

from app.core.deps import require_restaurant_owner
from app.db.database import get_db
from app.models.food import AddOn, FoodCategory, FoodItem
from app.models.restaurant import Restaurant
from app.models.user import User, UserRole
from app.schemas.food import (
    AddOnCreate,
    AddOnOut,
    FoodCategoryCreate,
    FoodCategoryOut,
    FoodItemCreate,
    FoodItemOut,
    FoodItemUpdate,
)

router = APIRouter(tags=["Menu"])


def _get_owned_restaurant(restaurant_id: uuid.UUID, db: Session, current_user: User) -> Restaurant:
    restaurant = db.query(Restaurant).filter(Restaurant.id == restaurant_id).first()
    if not restaurant:
        raise HTTPException(status_code=404, detail="Restaurant not found")
    if current_user.role != UserRole.admin and restaurant.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not your restaurant")
    return restaurant


# ---------- Public: view menu ----------
@router.get("/api/restaurants/{restaurant_id}/menu", response_model=List[FoodItemOut], tags=["Restaurants"])
def get_menu(restaurant_id: uuid.UUID, db: Session = Depends(get_db)):
    items = (
        db.query(FoodItem)
        .options(joinedload(FoodItem.add_ons))
        .filter(FoodItem.restaurant_id == restaurant_id, FoodItem.is_available == True)  # noqa: E712
        .all()
    )
    return items


@router.get("/api/restaurants/{restaurant_id}/categories", response_model=List[FoodCategoryOut], tags=["Restaurants"])
def get_categories(restaurant_id: uuid.UUID, db: Session = Depends(get_db)):
    return (
        db.query(FoodCategory)
        .filter(FoodCategory.restaurant_id == restaurant_id)
        .order_by(FoodCategory.display_order)
        .all()
    )


# ---------- Owner: manage categories ----------
@router.post("/api/restaurants/{restaurant_id}/categories", response_model=FoodCategoryOut, status_code=201)
def create_category(restaurant_id: uuid.UUID, payload: FoodCategoryCreate, db: Session = Depends(get_db), current_user: User = Depends(require_restaurant_owner)):
    _get_owned_restaurant(restaurant_id, db, current_user)
    category = FoodCategory(restaurant_id=restaurant_id, **payload.model_dump())
    db.add(category)
    db.commit()
    db.refresh(category)
    return category


@router.delete("/api/categories/{category_id}", status_code=204)
def delete_category(category_id: uuid.UUID, db: Session = Depends(get_db), current_user: User = Depends(require_restaurant_owner)):
    category = db.query(FoodCategory).filter(FoodCategory.id == category_id).first()
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    _get_owned_restaurant(category.restaurant_id, db, current_user)
    db.delete(category)
    db.commit()
    return None


# ---------- Owner: manage food items ----------
@router.post("/api/restaurants/{restaurant_id}/items", response_model=FoodItemOut, status_code=201)
def create_food_item(restaurant_id: uuid.UUID, payload: FoodItemCreate, db: Session = Depends(get_db), current_user: User = Depends(require_restaurant_owner)):
    _get_owned_restaurant(restaurant_id, db, current_user)
    item = FoodItem(restaurant_id=restaurant_id, **payload.model_dump())
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@router.patch("/api/items/{item_id}", response_model=FoodItemOut)
def update_food_item(item_id: uuid.UUID, payload: FoodItemUpdate, db: Session = Depends(get_db), current_user: User = Depends(require_restaurant_owner)):
    item = db.query(FoodItem).filter(FoodItem.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Food item not found")
    _get_owned_restaurant(item.restaurant_id, db, current_user)
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(item, key, value)
    db.commit()
    db.refresh(item)
    return item


@router.delete("/api/items/{item_id}", status_code=204)
def delete_food_item(item_id: uuid.UUID, db: Session = Depends(get_db), current_user: User = Depends(require_restaurant_owner)):
    item = db.query(FoodItem).filter(FoodItem.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Food item not found")
    _get_owned_restaurant(item.restaurant_id, db, current_user)
    db.delete(item)
    db.commit()
    return None


# ---------- Owner: manage add-ons ----------
@router.post("/api/items/{item_id}/add-ons", response_model=AddOnOut, status_code=201)
def create_add_on(item_id: uuid.UUID, payload: AddOnCreate, db: Session = Depends(get_db), current_user: User = Depends(require_restaurant_owner)):
    item = db.query(FoodItem).filter(FoodItem.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Food item not found")
    _get_owned_restaurant(item.restaurant_id, db, current_user)
    add_on = AddOn(food_item_id=item_id, **payload.model_dump())
    db.add(add_on)
    db.commit()
    db.refresh(add_on)
    return add_on


@router.delete("/api/add-ons/{add_on_id}", status_code=204)
def delete_add_on(add_on_id: uuid.UUID, db: Session = Depends(get_db), current_user: User = Depends(require_restaurant_owner)):
    add_on = db.query(AddOn).filter(AddOn.id == add_on_id).first()
    if not add_on:
        raise HTTPException(status_code=404, detail="Add-on not found")
    item = db.query(FoodItem).filter(FoodItem.id == add_on.food_item_id).first()
    _get_owned_restaurant(item.restaurant_id, db, current_user)
    db.delete(add_on)
    db.commit()
    return None
