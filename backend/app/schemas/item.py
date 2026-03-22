from datetime import datetime, date
from typing import Optional
from pydantic import BaseModel


class ItemBase(BaseModel):
    name: str
    quantity: int = 1
    price: float = 0.0
    purchase_date: Optional[date] = None
    expiry_date: Optional[date] = None
    category_id: Optional[int] = None
    location: Optional[str] = None
    notes: Optional[str] = None
    usage: Optional[str] = None
    purchase_channel: Optional[str] = None


class ItemCreate(ItemBase):
    pass


class ItemUpdate(BaseModel):
    name: Optional[str] = None
    quantity: Optional[int] = None
    price: Optional[float] = None
    purchase_date: Optional[date] = None
    expiry_date: Optional[date] = None
    category_id: Optional[int] = None
    location: Optional[str] = None
    notes: Optional[str] = None
    usage: Optional[str] = None
    purchase_channel: Optional[str] = None


class ItemResponse(ItemBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ItemListResponse(BaseModel):
    items: list[ItemResponse]
    total: int
