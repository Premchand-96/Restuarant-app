import enum
import uuid

from sqlalchemy import Column, String, Float, Boolean, ForeignKey, DateTime, func, Integer, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db.database import Base


class DiscountType(str, enum.Enum):
    flat = "flat"
    percentage = "percentage"


class Coupon(Base):
    __tablename__ = "coupons"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    restaurant_id = Column(UUID(as_uuid=True), ForeignKey("restaurants.id", ondelete="CASCADE"), nullable=True)  # null = platform-wide
    code = Column(String, unique=True, index=True, nullable=False)
    discount_type = Column(Enum(DiscountType), default=DiscountType.flat)
    discount_value = Column(Float, nullable=False)
    max_discount = Column(Float, nullable=True)
    min_order_amount = Column(Float, default=0.0)
    usage_limit = Column(Integer, nullable=True)
    times_used = Column(Integer, default=0)
    valid_from = Column(DateTime(timezone=True), server_default=func.now())
    valid_until = Column(DateTime(timezone=True), nullable=True)
    is_active = Column(Boolean, default=True)

    restaurant = relationship("Restaurant", back_populates="coupons")
