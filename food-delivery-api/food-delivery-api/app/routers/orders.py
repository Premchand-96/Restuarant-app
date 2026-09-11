import random
import string
import uuid
from datetime import datetime, timezone
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload

from app.core.deps import get_current_user, require_delivery_partner, require_restaurant_owner
from app.db.database import get_db
from app.models.address import Address
from app.models.cart import Cart, CartItem
from app.models.coupon import Coupon, DiscountType
from app.models.delivery_partner import DeliveryPartner
from app.models.order import Order, OrderItem, OrderItemAddOn, OrderStatus
from app.models.payment import Payment, PaymentMethod, PaymentStatus
from app.models.restaurant import Restaurant
from app.models.user import User, UserRole
from app.routers.cart import BASE_DELIVERY_FEE, TAX_RATE
from app.routers.cart import _serialize_cart
from app.schemas.cart import CartOut
from app.schemas.order import OrderCancelRequest, OrderOut, OrderStatusUpdate, PlaceOrderRequest

router = APIRouter(prefix="/api/orders", tags=["Orders"])

# Valid forward transitions a restaurant/delivery partner can make
NEXT_STATUS = {
    OrderStatus.placed: [OrderStatus.accepted, OrderStatus.rejected],
    OrderStatus.accepted: [OrderStatus.preparing],
    OrderStatus.preparing: [OrderStatus.ready_for_pickup],
    OrderStatus.ready_for_pickup: [OrderStatus.picked_up],
    OrderStatus.picked_up: [OrderStatus.out_for_delivery],
    OrderStatus.out_for_delivery: [OrderStatus.delivered],
}


def _generate_order_number() -> str:
    return "ORD" + "".join(random.choices(string.digits, k=8))


@router.post("", response_model=OrderOut, status_code=201)
def place_order(payload: PlaceOrderRequest, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    cart = (
        db.query(Cart)
        .options(joinedload(Cart.items).joinedload(CartItem.food_item), joinedload(Cart.items).joinedload(CartItem.add_ons))
        .filter(Cart.user_id == current_user.id)
        .first()
    )
    if not cart or not cart.items:
        raise HTTPException(status_code=400, detail="Your cart is empty")

    address = db.query(Address).filter(Address.id == payload.delivery_address_id, Address.user_id == current_user.id).first()
    if not address:
        raise HTTPException(status_code=404, detail="Delivery address not found")

    restaurant = db.query(Restaurant).filter(Restaurant.id == cart.restaurant_id).first()
    if not restaurant or not restaurant.is_open:
        raise HTTPException(status_code=400, detail="Restaurant is currently closed")

    subtotal = 0.0
    for ci in cart.items:
        add_on_total = sum(a.add_on.price for a in ci.add_ons)
        subtotal += (ci.food_item.price + add_on_total) * ci.quantity

    if subtotal < restaurant.min_order_amount:
        raise HTTPException(status_code=400, detail=f"Minimum order amount is {restaurant.min_order_amount}")

    coupon = db.query(Coupon).filter(Coupon.id == cart.coupon_id).first() if cart.coupon_id else None
    discount = 0.0
    if coupon and coupon.is_active and subtotal >= coupon.min_order_amount:
        if coupon.discount_type == DiscountType.flat:
            discount = coupon.discount_value
        else:
            discount = subtotal * (coupon.discount_value / 100.0)
            if coupon.max_discount:
                discount = min(discount, coupon.max_discount)
        discount = min(discount, subtotal)

    delivery_fee = BASE_DELIVERY_FEE
    taxable_amount = max(subtotal - discount, 0.0)
    tax = round(taxable_amount * TAX_RATE, 2)
    total = round(taxable_amount + delivery_fee + tax, 2)

    order = Order(
        order_number=_generate_order_number(),
        customer_id=current_user.id,
        restaurant_id=restaurant.id,
        delivery_address_id=address.id,
        subtotal=round(subtotal, 2),
        discount=round(discount, 2),
        delivery_fee=delivery_fee,
        tax=tax,
        total=total,
        coupon_id=coupon.id if coupon else None,
        delivery_instructions=payload.delivery_instructions,
        status=OrderStatus.placed,
    )
    db.add(order)
    db.flush()

    for ci in cart.items:
        order_item = OrderItem(
            order_id=order.id,
            food_item_id=ci.food_item_id,
            name_snapshot=ci.food_item.name,
            price_snapshot=ci.food_item.price,
            quantity=ci.quantity,
        )
        db.add(order_item)
        db.flush()
        for a in ci.add_ons:
            db.add(OrderItemAddOn(order_item_id=order_item.id, name_snapshot=a.add_on.name, price_snapshot=a.add_on.price))

    payment_status = PaymentStatus.pending if payload.payment_method == PaymentMethod.cash_on_delivery else PaymentStatus.success
    payment = Payment(order_id=order.id, method=payload.payment_method, status=payment_status, amount=total)
    db.add(payment)

    if coupon:
        coupon.times_used += 1

    # Clear cart after successful checkout
    db.query(CartItem).filter(CartItem.cart_id == cart.id).delete()
    cart.restaurant_id = None
    cart.coupon_id = None

    db.commit()
    db.refresh(order)
    return order


@router.get("", response_model=List[OrderOut])
def list_my_orders(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if current_user.role == UserRole.restaurant_owner:
        restaurant = db.query(Restaurant).filter(Restaurant.owner_id == current_user.id).first()
        if not restaurant:
            return []
        return db.query(Order).filter(Order.restaurant_id == restaurant.id).order_by(Order.placed_at.desc()).all()

    if current_user.role == UserRole.delivery_partner:
        partner = db.query(DeliveryPartner).filter(DeliveryPartner.user_id == current_user.id).first()
        if not partner:
            return []
        return db.query(Order).filter(Order.delivery_partner_id == partner.id).order_by(Order.placed_at.desc()).all()

    return db.query(Order).filter(Order.customer_id == current_user.id).order_by(Order.placed_at.desc()).all()


@router.get("/available-for-pickup", response_model=List[OrderOut])
def list_available_orders(db: Session = Depends(get_db), current_user: User = Depends(require_delivery_partner)):
    """Orders ready for pickup and not yet claimed by a delivery partner."""
    return (
        db.query(Order)
        .filter(Order.status == OrderStatus.ready_for_pickup, Order.delivery_partner_id.is_(None))
        .order_by(Order.placed_at.asc())
        .all()
    )


def _authorize_order_access(order: Order, db: Session, current_user: User) -> None:
    if current_user.role == UserRole.admin:
        return
    if current_user.role == UserRole.customer and order.customer_id == current_user.id:
        return
    if current_user.role == UserRole.restaurant_owner:
        restaurant = db.query(Restaurant).filter(Restaurant.id == order.restaurant_id).first()
        if restaurant and restaurant.owner_id == current_user.id:
            return
    if current_user.role == UserRole.delivery_partner:
        partner = db.query(DeliveryPartner).filter(DeliveryPartner.user_id == current_user.id).first()
        if partner and order.delivery_partner_id == partner.id:
            return
    raise HTTPException(status_code=403, detail="You do not have access to this order")


@router.get("/{order_id}", response_model=OrderOut)
def get_order(order_id: uuid.UUID, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    _authorize_order_access(order, db, current_user)
    return order


@router.patch("/{order_id}/status", response_model=OrderOut)
def update_order_status(order_id: uuid.UUID, payload: OrderStatusUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    _authorize_order_access(order, db, current_user)

    if order.status in (OrderStatus.delivered, OrderStatus.cancelled, OrderStatus.rejected):
        raise HTTPException(status_code=400, detail=f"Order already {order.status.value}, cannot change status")

    allowed_next = NEXT_STATUS.get(order.status, [])
    if payload.status not in allowed_next:
        raise HTTPException(status_code=400, detail=f"Cannot transition from {order.status.value} to {payload.status.value}. Allowed: {[s.value for s in allowed_next]}")

    now = datetime.now(timezone.utc)
    order.status = payload.status
    if payload.status == OrderStatus.accepted:
        order.accepted_at = now
    elif payload.status == OrderStatus.ready_for_pickup:
        order.ready_at = now
    elif payload.status == OrderStatus.picked_up:
        order.picked_up_at = now
        # auto-assign the delivery partner claiming pickup
        if current_user.role == UserRole.delivery_partner:
            partner = db.query(DeliveryPartner).filter(DeliveryPartner.user_id == current_user.id).first()
            if partner:
                order.delivery_partner_id = partner.id
    elif payload.status == OrderStatus.delivered:
        order.delivered_at = now
        if order.delivery_partner_id:
            partner = db.query(DeliveryPartner).filter(DeliveryPartner.id == order.delivery_partner_id).first()
            if partner:
                partner.total_deliveries = (partner.total_deliveries or 0) + 1
        payment = db.query(Payment).filter(Payment.order_id == order.id).first()
        if payment and payment.status == PaymentStatus.pending:
            payment.status = PaymentStatus.success
    elif payload.status == OrderStatus.rejected:
        order.cancel_reason = payload.cancel_reason or "Rejected by restaurant"

    db.commit()
    db.refresh(order)
    return order


@router.post("/{order_id}/claim", response_model=OrderOut)
def claim_order_for_delivery(order_id: uuid.UUID, db: Session = Depends(get_db), current_user: User = Depends(require_delivery_partner)):
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    if order.status != OrderStatus.ready_for_pickup or order.delivery_partner_id is not None:
        raise HTTPException(status_code=400, detail="Order not available for pickup")

    partner = db.query(DeliveryPartner).filter(DeliveryPartner.user_id == current_user.id).first()
    if not partner:
        raise HTTPException(status_code=400, detail="You must complete your delivery partner profile first")

    order.delivery_partner_id = partner.id
    db.commit()
    db.refresh(order)
    return order


@router.post("/{order_id}/cancel", response_model=OrderOut)
def cancel_order(order_id: uuid.UUID, payload: OrderCancelRequest, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    _authorize_order_access(order, db, current_user)

    if order.status not in (OrderStatus.placed, OrderStatus.accepted):
        raise HTTPException(status_code=400, detail="Order can no longer be cancelled at this stage")

    order.status = OrderStatus.cancelled
    order.cancel_reason = payload.reason or "Cancelled by customer"

    payment = db.query(Payment).filter(Payment.order_id == order.id).first()
    if payment and payment.status == PaymentStatus.success:
        payment.status = PaymentStatus.refunded

    db.commit()
    db.refresh(order)
    return order


@router.post("/{order_id}/reorder", response_model=CartOut, status_code=201)
def reorder(order_id: uuid.UUID, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Copies a previous order's items back into the user's cart. Returns the updated cart —
    call POST /api/orders separately to place a new order from it."""
    old_order = db.query(Order).options(joinedload(Order.items)).filter(Order.id == order_id, Order.customer_id == current_user.id).first()
    if not old_order:
        raise HTTPException(status_code=404, detail="Order not found")

    cart = db.query(Cart).filter(Cart.user_id == current_user.id).first()
    if not cart:
        cart = Cart(user_id=current_user.id)
        db.add(cart)
        db.flush()

    db.query(CartItem).filter(CartItem.cart_id == cart.id).delete()
    cart.restaurant_id = old_order.restaurant_id
    cart.coupon_id = None
    db.flush()

    for oi in old_order.items:
        if oi.food_item_id:
            db.add(CartItem(cart_id=cart.id, food_item_id=oi.food_item_id, quantity=oi.quantity))

    db.commit()
    return _serialize_cart(db, cart)
