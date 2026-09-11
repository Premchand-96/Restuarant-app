import uuid

from sqlalchemy import Column, String, Float, Boolean, ForeignKey, DateTime, func, Integer, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db.database import Base


class FoodCategory(Base):
    __tablename__ = "food_categories"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    restaurant_id = Column(UUID(as_uuid=True), ForeignKey("restaurants.id", ondelete="CASCADE"), nullable=False)
    name = Column(String, nullable=False)
    display_order = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    restaurant = relationship("Restaurant", back_populates="categories")
    food_items = relationship("FoodItem", back_populates="category")


class FoodItem(Base):
    __tablename__ = "food_items"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    restaurant_id = Column(UUID(as_uuid=True), ForeignKey("restaurants.id", ondelete="CASCADE"), nullable=False)
    category_id = Column(UUID(as_uuid=True), ForeignKey("food_categories.id", ondelete="SET NULL"), nullable=True)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    price = Column(Float, nullable=False)
    image_url = Column(String, nullable=True)
    is_veg = Column(Boolean, default=True)
    is_available = Column(Boolean, default=True)
    avg_rating = Column(Float, default=0.0)
    rating_count = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    restaurant = relationship("Restaurant", back_populates="food_items")
    category = relationship("FoodCategory", back_populates="food_items")
    add_ons = relationship("AddOn", back_populates="food_item", cascade="all, delete-orphan")


class AddOn(Base):
    __tablename__ = "add_ons"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    food_item_id = Column(UUID(as_uuid=True), ForeignKey("food_items.id", ondelete="CASCADE"), nullable=False)
    name = Column(String, nullable=False)
    price = Column(Float, default=0.0)
    is_available = Column(Boolean, default=True)

    food_item = relationship("FoodItem", back_populates="add_ons")
