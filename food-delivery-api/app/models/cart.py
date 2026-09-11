import uuid

from sqlalchemy import Column, ForeignKey, DateTime, func, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db.database import Base


class Cart(Base):
    __tablename__ = "carts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    restaurant_id = Column(UUID(as_uuid=True), ForeignKey("restaurants.id", ondelete="CASCADE"), nullable=True)
    coupon_id = Column(UUID(as_uuid=True), ForeignKey("coupons.id", ondelete="SET NULL"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    user = relationship("User", back_populates="cart")
    restaurant = relationship("Restaurant")
    coupon = relationship("Coupon")
    items = relationship("CartItem", back_populates="cart", cascade="all, delete-orphan")


class CartItem(Base):
    __tablename__ = "cart_items"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    cart_id = Column(UUID(as_uuid=True), ForeignKey("carts.id", ondelete="CASCADE"), nullable=False)
    food_item_id = Column(UUID(as_uuid=True), ForeignKey("food_items.id", ondelete="CASCADE"), nullable=False)
    quantity = Column(Integer, default=1)

    cart = relationship("Cart", back_populates="items")
    food_item = relationship("FoodItem")
    add_ons = relationship("CartItemAddOn", back_populates="cart_item", cascade="all, delete-orphan")


class CartItemAddOn(Base):
    __tablename__ = "cart_item_add_ons"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    cart_item_id = Column(UUID(as_uuid=True), ForeignKey("cart_items.id", ondelete="CASCADE"), nullable=False)
    add_on_id = Column(UUID(as_uuid=True), ForeignKey("add_ons.id", ondelete="CASCADE"), nullable=False)

    cart_item = relationship("CartItem", back_populates="add_ons")
    add_on = relationship("AddOn")
