import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload

from app.core.deps import get_current_user
from app.db.database import get_db
from app.models.cart import Cart, CartItem, CartItemAddOn
from app.models.coupon import Coupon, DiscountType
from app.models.food import AddOn, FoodItem
from app.models.user import User
from app.schemas.cart import (
    ApplyCouponRequest,
    CartItemAddOnOut,
    CartItemAddRequest,
    CartItemOut,
    CartItemUpdateRequest,
    CartOut,
)

router = APIRouter(prefix="/api/cart", tags=["Cart"])

TAX_RATE = 0.05  # 5% flat tax for simplicity
BASE_DELIVERY_FEE = 30.0


def _get_or_create_cart(db: Session, user: User) -> Cart:
    cart = db.query(Cart).filter(Cart.user_id == user.id).first()
    if not cart:
        cart = Cart(user_id=user.id)
        db.add(cart)
        db.commit()
        db.refresh(cart)
    return cart


def _serialize_cart(db: Session, cart: Cart) -> CartOut:
    cart = (
        db.query(Cart)
        .options(
            joinedload(Cart.items).joinedload(CartItem.food_item),
            joinedload(Cart.items).joinedload(CartItem.add_ons).joinedload(CartItemAddOn.add_on),
            joinedload(Cart.restaurant),
            joinedload(Cart.coupon),
        )
        .filter(Cart.id == cart.id)
        .first()
    )

    item_outs = []
    subtotal = 0.0
    for ci in cart.items:
        add_on_total = sum(a.add_on.price for a in ci.add_ons)
        item_total = (ci.food_item.price + add_on_total) * ci.quantity
        subtotal += item_total
        item_outs.append(
            CartItemOut(
                id=ci.id,
                food_item_id=ci.food_item_id,
                name=ci.food_item.name,
                price=ci.food_item.price,
                quantity=ci.quantity,
                is_veg=ci.food_item.is_veg,
                image_url=ci.food_item.image_url,
                add_ons=[
                    CartItemAddOnOut(id=a.id, add_on_id=a.add_on_id, name=a.add_on.name, price=a.add_on.price)
                    for a in ci.add_ons
                ],
                item_total=round(item_total, 2),
            )
        )

    discount = 0.0
    coupon_code = None
    if cart.coupon and cart.coupon.is_active and subtotal >= cart.coupon.min_order_amount:
        coupon_code = cart.coupon.code
        if cart.coupon.discount_type == DiscountType.flat:
            discount = cart.coupon.discount_value
        else:
            discount = subtotal * (cart.coupon.discount_value / 100.0)
            if cart.coupon.max_discount:
                discount = min(discount, cart.coupon.max_discount)
        discount = min(discount, subtotal)

    delivery_fee = BASE_DELIVERY_FEE if subtotal > 0 else 0.0
    taxable_amount = max(subtotal - discount, 0.0)
    tax = round(taxable_amount * TAX_RATE, 2)
    total = round(taxable_amount + delivery_fee + tax, 2)

    return CartOut(
        id=cart.id,
        restaurant_id=cart.restaurant_id,
        restaurant_name=cart.restaurant.name if cart.restaurant else None,
        items=item_outs,
        coupon_code=coupon_code,
        subtotal=round(subtotal, 2),
        discount=round(discount, 2),
        delivery_fee=round(delivery_fee, 2),
        tax=tax,
        total=total,
    )


@router.get("", response_model=CartOut)
def view_cart(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    cart = _get_or_create_cart(db, current_user)
    return _serialize_cart(db, cart)


@router.post("/items", response_model=CartOut, status_code=201)
def add_item_to_cart(payload: CartItemAddRequest, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    food_item = db.query(FoodItem).filter(FoodItem.id == payload.food_item_id, FoodItem.is_available == True).first()  # noqa: E712
    if not food_item:
        raise HTTPException(status_code=404, detail="Food item not found or unavailable")

    cart = _get_or_create_cart(db, current_user)

    # Enforce single-restaurant cart: switching restaurants clears the cart
    if cart.restaurant_id and cart.restaurant_id != food_item.restaurant_id:
        db.query(CartItem).filter(CartItem.cart_id == cart.id).delete()
        cart.restaurant_id = food_item.restaurant_id
        cart.coupon_id = None
        db.commit()
    elif not cart.restaurant_id:
        cart.restaurant_id = food_item.restaurant_id
        db.commit()

    if payload.add_on_ids:
        valid_add_ons = db.query(AddOn).filter(AddOn.id.in_(payload.add_on_ids), AddOn.food_item_id == food_item.id).all()
        if len(valid_add_ons) != len(payload.add_on_ids):
            raise HTTPException(status_code=400, detail="One or more add-ons are invalid for this item")

    cart_item = CartItem(cart_id=cart.id, food_item_id=food_item.id, quantity=max(payload.quantity, 1))
    db.add(cart_item)
    db.flush()

    for add_on_id in payload.add_on_ids:
        db.add(CartItemAddOn(cart_item_id=cart_item.id, add_on_id=add_on_id))

    db.commit()
    return _serialize_cart(db, cart)


@router.patch("/items/{cart_item_id}", response_model=CartOut)
def update_cart_item(cart_item_id: uuid.UUID, payload: CartItemUpdateRequest, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    cart = _get_or_create_cart(db, current_user)
    cart_item = db.query(CartItem).filter(CartItem.id == cart_item_id, CartItem.cart_id == cart.id).first()
    if not cart_item:
        raise HTTPException(status_code=404, detail="Cart item not found")

    if payload.quantity <= 0:
        db.delete(cart_item)
    else:
        cart_item.quantity = payload.quantity
    db.commit()
    return _serialize_cart(db, cart)


@router.delete("/items/{cart_item_id}", response_model=CartOut)
def remove_cart_item(cart_item_id: uuid.UUID, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    cart = _get_or_create_cart(db, current_user)
    cart_item = db.query(CartItem).filter(CartItem.id == cart_item_id, CartItem.cart_id == cart.id).first()
    if not cart_item:
        raise HTTPException(status_code=404, detail="Cart item not found")
    db.delete(cart_item)
    db.commit()
    return _serialize_cart(db, cart)


@router.post("/coupon", response_model=CartOut)
def apply_coupon(payload: ApplyCouponRequest, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    cart = _get_or_create_cart(db, current_user)
    coupon = db.query(Coupon).filter(Coupon.code == payload.code, Coupon.is_active == True).first()  # noqa: E712
    if not coupon:
        raise HTTPException(status_code=404, detail="Invalid coupon code")
    if coupon.restaurant_id and coupon.restaurant_id != cart.restaurant_id:
        raise HTTPException(status_code=400, detail="Coupon not valid for items in your cart")
    if coupon.valid_until and coupon.valid_until.replace(tzinfo=timezone.utc) < datetime.now(timezone.utc):
        raise HTTPException(status_code=400, detail="Coupon has expired")
    if coupon.usage_limit is not None and coupon.times_used >= coupon.usage_limit:
        raise HTTPException(status_code=400, detail="Coupon usage limit reached")

    cart.coupon_id = coupon.id
    db.commit()
    return _serialize_cart(db, cart)


@router.delete("/coupon", response_model=CartOut)
def remove_coupon(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    cart = _get_or_create_cart(db, current_user)
    cart.coupon_id = None
    db.commit()
    return _serialize_cart(db, cart)


@router.delete("", status_code=204)
def clear_cart(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    cart = _get_or_create_cart(db, current_user)
    db.query(CartItem).filter(CartItem.cart_id == cart.id).delete()
    cart.restaurant_id = None
    cart.coupon_id = None
    db.commit()
    return None
