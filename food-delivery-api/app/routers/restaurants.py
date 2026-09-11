import uuid
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.core.deps import get_current_user, require_admin, require_restaurant_owner
from app.db.database import get_db
from app.models.restaurant import Restaurant, RestaurantStatus
from app.models.user import User, UserRole
from app.schemas.restaurant import RestaurantCreate, RestaurantOut, RestaurantStatusUpdate, RestaurantUpdate

router = APIRouter(prefix="/api/restaurants", tags=["Restaurants"])


# ---------- Public browse ----------
@router.get("", response_model=List[RestaurantOut])
def list_restaurants(
    city: Optional[str] = None,
    search: Optional[str] = None,
    cuisine: Optional[str] = None,
    is_veg_only: Optional[bool] = None,
    min_rating: Optional[float] = Query(None, ge=0, le=5),
    sort_by: Optional[str] = Query(None, description="rating | delivery_time"),
    db: Session = Depends(get_db),
):
    query = db.query(Restaurant).filter(Restaurant.status == RestaurantStatus.approved)

    if city:
        query = query.filter(Restaurant.city.ilike(f"%{city}%"))
    if search:
        query = query.filter(or_(Restaurant.name.ilike(f"%{search}%"), Restaurant.cuisine.ilike(f"%{search}%")))
    if cuisine:
        query = query.filter(Restaurant.cuisine.ilike(f"%{cuisine}%"))
    if is_veg_only is not None:
        query = query.filter(Restaurant.is_veg_only == is_veg_only)
    if min_rating is not None:
        query = query.filter(Restaurant.avg_rating >= min_rating)

    if sort_by == "rating":
        query = query.order_by(Restaurant.avg_rating.desc())
    elif sort_by == "delivery_time":
        query = query.order_by(Restaurant.avg_delivery_time_minutes.asc())

    return query.all()


# IMPORTANT: this must be declared BEFORE the /{restaurant_id} route below,
# otherwise FastAPI/Starlette will try to match "me" against the path param first.
@router.get("/me/mine", response_model=RestaurantOut)
def get_my_restaurant(db: Session = Depends(get_db), current_user: User = Depends(require_restaurant_owner)):
    restaurant = db.query(Restaurant).filter(Restaurant.owner_id == current_user.id).first()
    if not restaurant:
        raise HTTPException(status_code=404, detail="You don't have a restaurant yet")
    return restaurant


@router.get("/{restaurant_id}", response_model=RestaurantOut)
def get_restaurant(restaurant_id: uuid.UUID, db: Session = Depends(get_db)):
    restaurant = db.query(Restaurant).filter(Restaurant.id == restaurant_id).first()
    if not restaurant:
        raise HTTPException(status_code=404, detail="Restaurant not found")
    return restaurant


# ---------- Restaurant owner management ----------
@router.post("", response_model=RestaurantOut, status_code=201)
def register_restaurant(payload: RestaurantCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if current_user.role not in (UserRole.restaurant_owner, UserRole.admin):
        raise HTTPException(status_code=403, detail="Only restaurant owners can register a restaurant")

    existing = db.query(Restaurant).filter(Restaurant.owner_id == current_user.id).first()
    if existing:
        raise HTTPException(status_code=400, detail="You already have a registered restaurant")

    restaurant = Restaurant(owner_id=current_user.id, **payload.model_dump())
    db.add(restaurant)
    db.commit()
    db.refresh(restaurant)
    return restaurant


def _get_owned_restaurant(restaurant_id: uuid.UUID, db: Session, current_user: User) -> Restaurant:
    restaurant = db.query(Restaurant).filter(Restaurant.id == restaurant_id).first()
    if not restaurant:
        raise HTTPException(status_code=404, detail="Restaurant not found")
    if current_user.role != UserRole.admin and restaurant.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not your restaurant")
    return restaurant


@router.patch("/{restaurant_id}", response_model=RestaurantOut)
def update_restaurant(restaurant_id: uuid.UUID, payload: RestaurantUpdate, db: Session = Depends(get_db), current_user: User = Depends(require_restaurant_owner)):
    restaurant = _get_owned_restaurant(restaurant_id, db, current_user)
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(restaurant, key, value)
    db.commit()
    db.refresh(restaurant)
    return restaurant


@router.delete("/{restaurant_id}", status_code=204)
def delete_restaurant(restaurant_id: uuid.UUID, db: Session = Depends(get_db), current_user: User = Depends(require_restaurant_owner)):
    restaurant = _get_owned_restaurant(restaurant_id, db, current_user)
    db.delete(restaurant)
    db.commit()
    return None


# ---------- Admin ----------
@router.patch("/{restaurant_id}/status", response_model=RestaurantOut)
def update_restaurant_status(restaurant_id: uuid.UUID, payload: RestaurantStatusUpdate, db: Session = Depends(get_db), current_user: User = Depends(require_admin)):
    restaurant = db.query(Restaurant).filter(Restaurant.id == restaurant_id).first()
    if not restaurant:
        raise HTTPException(status_code=404, detail="Restaurant not found")
    restaurant.status = payload.status
    db.commit()
    db.refresh(restaurant)
    return restaurant
