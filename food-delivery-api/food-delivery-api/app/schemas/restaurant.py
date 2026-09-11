import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict

from app.models.restaurant import RestaurantStatus


class RestaurantBase(BaseModel):
    name: str
    description: Optional[str] = None
    cuisine: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    address_line: str
    city: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    is_veg_only: bool = False
    min_order_amount: float = 0.0
    avg_delivery_time_minutes: float = 30


class RestaurantCreate(RestaurantBase):
    pass


class RestaurantUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    cuisine: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    address_line: Optional[str] = None
    city: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    logo_url: Optional[str] = None
    banner_url: Optional[str] = None
    is_veg_only: Optional[bool] = None
    is_open: Optional[bool] = None
    min_order_amount: Optional[float] = None
    avg_delivery_time_minutes: Optional[float] = None


class RestaurantOut(RestaurantBase):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    owner_id: uuid.UUID
    logo_url: Optional[str] = None
    banner_url: Optional[str] = None
    avg_rating: float
    rating_count: float
    is_open: bool
    status: RestaurantStatus
    created_at: datetime


class RestaurantStatusUpdate(BaseModel):
    status: RestaurantStatus
