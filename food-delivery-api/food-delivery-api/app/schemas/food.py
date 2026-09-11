import uuid
from typing import Optional, List

from pydantic import BaseModel, ConfigDict


# ---- Category ----
class FoodCategoryBase(BaseModel):
    name: str
    display_order: int = 0


class FoodCategoryCreate(FoodCategoryBase):
    pass


class FoodCategoryOut(FoodCategoryBase):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    restaurant_id: uuid.UUID


# ---- AddOn ----
class AddOnBase(BaseModel):
    name: str
    price: float = 0.0
    is_available: bool = True


class AddOnCreate(AddOnBase):
    pass


class AddOnOut(AddOnBase):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    food_item_id: uuid.UUID


# ---- FoodItem ----
class FoodItemBase(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    image_url: Optional[str] = None
    is_veg: bool = True
    category_id: Optional[uuid.UUID] = None


class FoodItemCreate(FoodItemBase):
    pass


class FoodItemUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    image_url: Optional[str] = None
    is_veg: Optional[bool] = None
    is_available: Optional[bool] = None
    category_id: Optional[uuid.UUID] = None


class FoodItemOut(FoodItemBase):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    restaurant_id: uuid.UUID
    is_available: bool
    avg_rating: float
    rating_count: int
    add_ons: List[AddOnOut] = []
