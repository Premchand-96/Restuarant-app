import uuid
from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel, ConfigDict

from app.models.order import OrderStatus
from app.models.payment import PaymentMethod


class PlaceOrderRequest(BaseModel):
    delivery_address_id: uuid.UUID
    payment_method: PaymentMethod
    delivery_instructions: Optional[str] = None


class OrderItemAddOnOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    name_snapshot: str
    price_snapshot: float


class OrderItemOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    name_snapshot: str
    price_snapshot: float
    quantity: int
    add_ons: List[OrderItemAddOnOut] = []


class OrderOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    order_number: str
    restaurant_id: Optional[uuid.UUID] = None
    customer_id: Optional[uuid.UUID] = None
    delivery_partner_id: Optional[uuid.UUID] = None
    subtotal: float
    discount: float
    delivery_fee: float
    tax: float
    total: float
    status: OrderStatus
    delivery_instructions: Optional[str] = None
    cancel_reason: Optional[str] = None
    placed_at: datetime
    delivered_at: Optional[datetime] = None
    items: List[OrderItemOut] = []


class OrderStatusUpdate(BaseModel):
    status: OrderStatus
    cancel_reason: Optional[str] = None


class OrderCancelRequest(BaseModel):
    reason: Optional[str] = None
