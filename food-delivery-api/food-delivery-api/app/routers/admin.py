import uuid
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.deps import require_admin
from app.db.database import get_db
from app.models.order import Order, OrderStatus
from app.models.payment import Payment, PaymentStatus
from app.models.restaurant import Restaurant, RestaurantStatus
from app.models.user import User, UserRole
from app.schemas.user import UserOut

router = APIRouter(prefix="/api/admin", tags=["Admin"])


@router.get("/dashboard")
def dashboard_stats(db: Session = Depends(get_db), current_user: User = Depends(require_admin)):
    total_users = db.query(func.count(User.id)).scalar()
    total_restaurants = db.query(func.count(Restaurant.id)).scalar()
    pending_restaurants = db.query(func.count(Restaurant.id)).filter(Restaurant.status == RestaurantStatus.pending).scalar()
    total_orders = db.query(func.count(Order.id)).scalar()
    active_orders = (
        db.query(func.count(Order.id))
        .filter(Order.status.notin_([OrderStatus.delivered, OrderStatus.cancelled, OrderStatus.rejected]))
        .scalar()
    )
    total_revenue = (
        db.query(func.coalesce(func.sum(Payment.amount), 0.0))
        .filter(Payment.status == PaymentStatus.success)
        .scalar()
    )

    return {
        "total_users": total_users,
        "total_restaurants": total_restaurants,
        "pending_restaurant_approvals": pending_restaurants,
        "total_orders": total_orders,
        "active_orders": active_orders,
        "total_revenue": round(float(total_revenue), 2),
    }


@router.get("/users", response_model=List[UserOut])
def list_users(role: UserRole | None = None, db: Session = Depends(get_db), current_user: User = Depends(require_admin)):
    query = db.query(User)
    if role:
        query = query.filter(User.role == role)
    return query.order_by(User.created_at.desc()).all()


@router.patch("/users/{user_id}/deactivate", response_model=UserOut)
def deactivate_user(user_id: uuid.UUID, db: Session = Depends(get_db), current_user: User = Depends(require_admin)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.is_active = False
    db.commit()
    db.refresh(user)
    return user


@router.patch("/users/{user_id}/activate", response_model=UserOut)
def activate_user(user_id: uuid.UUID, db: Session = Depends(get_db), current_user: User = Depends(require_admin)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.is_active = True
    db.commit()
    db.refresh(user)
    return user


@router.get("/restaurants/pending")
def list_pending_restaurants(db: Session = Depends(get_db), current_user: User = Depends(require_admin)):
    restaurants = db.query(Restaurant).filter(Restaurant.status == RestaurantStatus.pending).all()
    return restaurants
