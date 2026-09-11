import uuid
from typing import Optional, List

from pydantic import BaseModel, ConfigDict


class CartItemAddRequest(BaseModel):
    food_item_id: uuid.UUID
    quantity: int = 1
    add_on_ids: List[uuid.UUID] = []


class CartItemUpdateRequest(BaseModel):
    quantity: int


class CartItemAddOnOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    add_on_id: uuid.UUID
    name: str
    price: float


class CartItemOut(BaseModel):
    id: uuid.UUID
    food_item_id: uuid.UUID
    name: str
    price: float
    quantity: int
    is_veg: bool
    image_url: Optional[str] = None
    add_ons: List[CartItemAddOnOut] = []
    item_total: float


class CartOut(BaseModel):
    id: uuid.UUID
    restaurant_id: Optional[uuid.UUID] = None
    restaurant_name: Optional[str] = None
    items: List[CartItemOut] = []
    coupon_code: Optional[str] = None
    subtotal: float
    discount: float
    delivery_fee: float
    tax: float
    total: float


class ApplyCouponRequest(BaseModel):
    code: str
