import enum
import uuid

from sqlalchemy import Column, String, Float, Boolean, ForeignKey, DateTime, Enum, func, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db.database import Base


class RestaurantStatus(str, enum.Enum):
    pending = "pending"
    approved = "approved"
    rejected = "rejected"
    suspended = "suspended"


class Restaurant(Base):
    __tablename__ = "restaurants"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    owner_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    cuisine = Column(String, nullable=True)
    phone = Column(String, nullable=True)
    email = Column(String, nullable=True)
    address_line = Column(String, nullable=False)
    city = Column(String, nullable=False)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    logo_url = Column(String, nullable=True)
    banner_url = Column(String, nullable=True)
    avg_rating = Column(Float, default=0.0)
    rating_count = Column(Float, default=0)
    is_veg_only = Column(Boolean, default=False)
    is_open = Column(Boolean, default=True)
    min_order_amount = Column(Float, default=0.0)
    avg_delivery_time_minutes = Column(Float, default=30)
    status = Column(Enum(RestaurantStatus), default=RestaurantStatus.pending)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    owner = relationship("User", back_populates="restaurant")
    categories = relationship("FoodCategory", back_populates="restaurant", cascade="all, delete-orphan")
    food_items = relationship("FoodItem", back_populates="restaurant", cascade="all, delete-orphan")
    orders = relationship("Order", back_populates="restaurant")
    reviews = relationship("Review", back_populates="restaurant")
    coupons = relationship("Coupon", back_populates="restaurant", cascade="all, delete-orphan")
