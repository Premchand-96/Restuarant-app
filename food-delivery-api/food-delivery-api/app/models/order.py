import enum
import uuid

from sqlalchemy import Column, String, Float, ForeignKey, DateTime, func, Integer, Enum, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db.database import Base


class OrderStatus(str, enum.Enum):
    placed = "placed"
    accepted = "accepted"
    preparing = "preparing"
    ready_for_pickup = "ready_for_pickup"
    picked_up = "picked_up"
    out_for_delivery = "out_for_delivery"
    delivered = "delivered"
    cancelled = "cancelled"
    rejected = "rejected"


class Order(Base):
    __tablename__ = "orders"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    order_number = Column(String, unique=True, index=True, nullable=False)
    customer_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    restaurant_id = Column(UUID(as_uuid=True), ForeignKey("restaurants.id", ondelete="SET NULL"), nullable=True)
    delivery_partner_id = Column(UUID(as_uuid=True), ForeignKey("delivery_partners.id", ondelete="SET NULL"), nullable=True)
    delivery_address_id = Column(UUID(as_uuid=True), ForeignKey("addresses.id", ondelete="SET NULL"), nullable=True)

    subtotal = Column(Float, nullable=False, default=0.0)
    discount = Column(Float, default=0.0)
    delivery_fee = Column(Float, default=0.0)
    tax = Column(Float, default=0.0)
    total = Column(Float, nullable=False, default=0.0)

    coupon_id = Column(UUID(as_uuid=True), ForeignKey("coupons.id", ondelete="SET NULL"), nullable=True)
    delivery_instructions = Column(Text, nullable=True)
    status = Column(Enum(OrderStatus), default=OrderStatus.placed, nullable=False)
    cancel_reason = Column(String, nullable=True)

    placed_at = Column(DateTime(timezone=True), server_default=func.now())
    accepted_at = Column(DateTime(timezone=True), nullable=True)
    ready_at = Column(DateTime(timezone=True), nullable=True)
    picked_up_at = Column(DateTime(timezone=True), nullable=True)
    delivered_at = Column(DateTime(timezone=True), nullable=True)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    customer = relationship("User", back_populates="orders")
    restaurant = relationship("Restaurant", back_populates="orders")
    delivery_partner = relationship("DeliveryPartner", back_populates="orders")
    delivery_address = relationship("Address")
    coupon = relationship("Coupon")
    items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")
    payment = relationship("Payment", back_populates="order", uselist=False, cascade="all, delete-orphan")
    review = relationship("Review", back_populates="order", uselist=False)


class OrderItem(Base):
    __tablename__ = "order_items"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    order_id = Column(UUID(as_uuid=True), ForeignKey("orders.id", ondelete="CASCADE"), nullable=False)
    food_item_id = Column(UUID(as_uuid=True), ForeignKey("food_items.id", ondelete="SET NULL"), nullable=True)
    name_snapshot = Column(String, nullable=False)  # preserve name at order time
    price_snapshot = Column(Float, nullable=False)  # preserve price at order time
    quantity = Column(Integer, default=1)

    order = relationship("Order", back_populates="items")
    food_item = relationship("FoodItem")
    add_ons = relationship("OrderItemAddOn", back_populates="order_item", cascade="all, delete-orphan")


class OrderItemAddOn(Base):
    __tablename__ = "order_item_add_ons"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    order_item_id = Column(UUID(as_uuid=True), ForeignKey("order_items.id", ondelete="CASCADE"), nullable=False)
    name_snapshot = Column(String, nullable=False)
    price_snapshot = Column(Float, nullable=False)

    order_item = relationship("OrderItem", back_populates="add_ons")
