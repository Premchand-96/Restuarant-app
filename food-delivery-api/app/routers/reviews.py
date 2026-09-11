import uuid
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.deps import get_current_user
from app.db.database import get_db
from app.models.order import Order, OrderStatus
from app.models.restaurant import Restaurant
from app.models.review import Review
from app.models.user import User
from app.schemas.misc import ReviewCreate, ReviewOut

router = APIRouter(tags=["Reviews"])


@router.post("/api/orders/{order_id}/review", response_model=ReviewOut, status_code=201)
def create_review(order_id: uuid.UUID, payload: ReviewCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    order = db.query(Order).filter(Order.id == order_id, Order.customer_id == current_user.id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    if order.status != OrderStatus.delivered:
        raise HTTPException(status_code=400, detail="You can only review delivered orders")

    existing = db.query(Review).filter(Review.order_id == order_id).first()
    if existing:
        raise HTTPException(status_code=400, detail="You already reviewed this order")

    review = Review(
        order_id=order_id,
        user_id=current_user.id,
        restaurant_id=order.restaurant_id,
        **payload.model_dump(),
    )
    db.add(review)

    if payload.restaurant_rating and order.restaurant_id:
        restaurant = db.query(Restaurant).filter(Restaurant.id == order.restaurant_id).first()
        if restaurant:
            total_score = restaurant.avg_rating * restaurant.rating_count + payload.restaurant_rating
            restaurant.rating_count += 1
            restaurant.avg_rating = round(total_score / restaurant.rating_count, 2)

    db.commit()
    db.refresh(review)
    return review


@router.get("/api/restaurants/{restaurant_id}/reviews", response_model=List[ReviewOut])
def list_restaurant_reviews(restaurant_id: uuid.UUID, db: Session = Depends(get_db)):
    return db.query(Review).filter(Review.restaurant_id == restaurant_id).order_by(Review.created_at.desc()).all()
