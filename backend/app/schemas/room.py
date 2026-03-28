from datetime import datetime
from pydantic import BaseModel
from typing import List

from app.schemas.item import ItemResponse


class RoomBase(BaseModel):
    name: str


class RoomCreate(RoomBase):
    pass


class RoomUpdate(RoomBase):
    pass

class RoomResponse(RoomBase):
    id: int
    user_id: int
    created_at: datetime

    class Config:
        from_attributes = True


class RoomListResponse(BaseModel):
    rooms: List[RoomResponse]
    total: int


class RoomWithItemsResponse(RoomBase):
    id: int
    user_id: int
    created_at: datetime
    items: List[ItemResponse]

    class Config:
        from_attributes = True
