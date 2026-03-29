from datetime import datetime
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload

from app.database import get_db
from app.models import User, Room
from app.schemas import RoomCreate, RoomUpdate, RoomResponse, RoomListResponse, RoomWithItemsResponse
from app.auth import get_current_user

router = APIRouter(prefix="/api/rooms", tags=["rooms"])


@router.get("", response_model=RoomListResponse)
def get_rooms(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    rooms = db.query(Room).filter(Room.user_id == current_user.id).all()
    total = len(rooms)
    return {"rooms": rooms, "total": total}


@router.post("", response_model=RoomResponse, status_code=status.HTTP_201_CREATED)
def create_room(
    room_data: RoomCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # 确保用户有默认家庭
    from app.routers.family import get_or_create_default_family
    default_family = get_or_create_default_family(current_user, db)
    
    new_room = Room(
        name=room_data.name,
        user_id=current_user.id,
        family_id=default_family.id
    )
    db.add(new_room)
    db.commit()
    db.refresh(new_room)
    return new_room


@router.get("/{room_id}", response_model=RoomResponse)
def get_room(
    room_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    room = db.query(Room).filter(Room.id == room_id, Room.user_id == current_user.id).first()
    if not room:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Room not found")
    return room


@router.put("/{room_id}", response_model=RoomResponse)
def update_room(
    room_id: int,
    room_data: RoomUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    room = db.query(Room).filter(Room.id == room_id, Room.user_id == current_user.id).first()
    if not room:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Room not found")
    room.name = room_data.name
    db.commit()
    db.refresh(room)
    return room


@router.delete("/{room_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_room(
    room_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    room = db.query(Room).filter(Room.id == room_id, Room.user_id == current_user.id).first()
    if not room:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Room not found")
    db.delete(room)
    db.commit()
    return None


@router.get("/{room_id}/items", response_model=RoomWithItemsResponse)
def get_room_items(
    room_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    room = db.query(Room).options(joinedload(Room.items)).filter(
        Room.id == room_id, Room.user_id == current_user.id
    ).first()
    if not room:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Room not found")
    return room
