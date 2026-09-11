import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.deps import get_current_user
from app.db.database import get_db
from app.models.order import Order
from app.models.payment import Payment
from app.models.user import User, UserRole
from app.schemas.misc import PaymentOut

router = APIRouter(prefix="/api/payments", tags=["Payments"])


@router.get("/order/{order_id}", response_model=PaymentOut)
def get_payment_for_order(order_id: uuid.UUID, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    if current_user.role != UserRole.admin and order.customer_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not your order")

    payment = db.query(Payment).filter(Payment.order_id == order_id).first()
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")
    return payment
