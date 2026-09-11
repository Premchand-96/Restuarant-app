import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict

from app.models.payment import PaymentMethod, PaymentStatus
from app.models.coupon import DiscountType
from app.models.delivery_partner import VehicleType


# ---- Payment ----
class PaymentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    order_id: uuid.UUID
    method: PaymentMethod
    status: PaymentStatus
    amount: float
    transaction_ref: Optional[str] = None


# ---- Coupon ----
class CouponBase(BaseModel):
    code: str
    discount_type: DiscountType = DiscountType.flat
    discount_value: float
    max_discount: Optional[float] = None
    min_order_amount: float = 0.0
    usage_limit: Optional[int] = None
    valid_until: Optional[datetime] = None


class CouponCreate(CouponBase):
    pass


class CouponOut(CouponBase):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    restaurant_id: Optional[uuid.UUID] = None
    times_used: int
    is_active: bool


# ---- Review ----
class ReviewCreate(BaseModel):
    restaurant_rating: Optional[int] = None
    food_rating: Optional[int] = None
    delivery_rating: Optional[int] = None
    comment: Optional[str] = None


class ReviewOut(ReviewCreate):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    order_id: uuid.UUID
    user_id: Optional[uuid.UUID] = None
    restaurant_id: Optional[uuid.UUID] = None
    created_at: datetime


# ---- Delivery Partner ----
class DeliveryPartnerCreate(BaseModel):
    vehicle_type: VehicleType = VehicleType.bike
    vehicle_number: Optional[str] = None
    license_number: Optional[str] = None


class DeliveryPartnerOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    user_id: uuid.UUID
    vehicle_type: VehicleType
    vehicle_number: Optional[str] = None
    is_online: bool
    is_verified: bool
    avg_rating: float
    total_deliveries: float


class DeliveryStatusUpdate(BaseModel):
    is_online: bool


class DeliveryLocationUpdate(BaseModel):
    latitude: float
    longitude: float


# ---- Notification ----
class NotificationOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    title: str
    message: Optional[str] = None
    is_read: bool
    created_at: datetime
