import uuid
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.deps import require_admin, require_restaurant_owner
from app.db.database import get_db
from app.models.coupon import Coupon
from app.models.restaurant import Restaurant
from app.models.user import User, UserRole
from app.schemas.misc import CouponCreate, CouponOut

router = APIRouter(prefix="/api/coupons", tags=["Coupons"])


@router.post("", response_model=CouponOut, status_code=201)
def create_coupon(payload: CouponCreate, restaurant_id: Optional[uuid.UUID] = None, db: Session = Depends(get_db), current_user: User = Depends(require_restaurant_owner)):
    if restaurant_id:
        restaurant = db.query(Restaurant).filter(Restaurant.id == restaurant_id).first()
        if not restaurant:
            raise HTTPException(status_code=404, detail="Restaurant not found")
        if current_user.role != UserRole.admin and restaurant.owner_id != current_user.id:
            raise HTTPException(status_code=403, detail="Not your restaurant")
    else:
        if current_user.role != UserRole.admin:
            raise HTTPException(status_code=403, detail="Only admins can create platform-wide coupons")

    existing = db.query(Coupon).filter(Coupon.code == payload.code).first()
    if existing:
        raise HTTPException(status_code=400, detail="Coupon code already exists")

    coupon = Coupon(restaurant_id=restaurant_id, **payload.model_dump())
    db.add(coupon)
    db.commit()
    db.refresh(coupon)
    return coupon


@router.get("/restaurant/{restaurant_id}", response_model=List[CouponOut])
def list_restaurant_coupons(restaurant_id: uuid.UUID, db: Session = Depends(get_db)):
    return db.query(Coupon).filter(Coupon.restaurant_id == restaurant_id, Coupon.is_active == True).all()  # noqa: E712


@router.delete("/{coupon_id}", status_code=204)
def deactivate_coupon(coupon_id: uuid.UUID, db: Session = Depends(get_db), current_user: User = Depends(require_restaurant_owner)):
    coupon = db.query(Coupon).filter(Coupon.id == coupon_id).first()
    if not coupon:
        raise HTTPException(status_code=404, detail="Coupon not found")
    if coupon.restaurant_id:
        restaurant = db.query(Restaurant).filter(Restaurant.id == coupon.restaurant_id).first()
        if current_user.role != UserRole.admin and (not restaurant or restaurant.owner_id != current_user.id):
            raise HTTPException(status_code=403, detail="Not your coupon")
    elif current_user.role != UserRole.admin:
        raise HTTPException(status_code=403, detail="Only admins can remove platform-wide coupons")

    coupon.is_active = False
    db.commit()
    return None
