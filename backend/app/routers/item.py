from datetime import date
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User, Item, Category, Room
from app.schemas import ItemCreate, ItemUpdate, ItemResponse, ItemListResponse
from app.auth import get_current_user

router = APIRouter(prefix="/api/items", tags=["items"])


@router.get("", response_model=ItemListResponse)
def get_items(
    name: Optional[str] = Query(None, description="Filter by item name"),
    category_id: Optional[int] = Query(None, description="Filter by category ID"),
    room_id: Optional[int] = Query(None, description="Filter by room ID"),
    expired: Optional[bool] = Query(None, description="Filter expired items"),
    expiring_soon: Optional[bool] = Query(None, description="Filter items expiring within 30 days"),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    query = db.query(Item).filter(Item.user_id == current_user.id)
    
    if name:
        query = query.filter(Item.name.ilike(f"%{name}%"))
    
    if category_id:
        query = query.filter(Item.category_id == category_id)
    
    if room_id:
        query = query.filter(Item.room_id == room_id)
    
    today = date.today()
    
    if expired is True:
        query = query.filter(Item.expiry_date < today)
    elif expired is False:
        query = query.filter((Item.expiry_date == None) | (Item.expiry_date >= today))
    
    if expiring_soon is True:
        thirty_days_later = today + __import__("datetime").timedelta(days=30)
        query = query.filter(
            Item.expiry_date != None,
            Item.expiry_date >= today,
            Item.expiry_date <= thirty_days_later
        )
    
    total = query.count()
    items = query.order_by(Item.created_at.desc()).offset(skip).limit(limit).all()
    
    return {"items": items, "total": total}


@router.get("/{item_id}", response_model=ItemResponse)
def get_item(
    item_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    item = db.query(Item).filter(
        Item.id == item_id,
        Item.user_id == current_user.id
    ).first()
    
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Item not found"
        )
    
    return item


@router.post("", response_model=ItemResponse, status_code=status.HTTP_201_CREATED)
def create_item(
    item_data: ItemCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if item_data.category_id:
        category = db.query(Category).filter(
            Category.id == item_data.category_id,
            Category.user_id == current_user.id
        ).first()
        if not category:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Category not found"
            )
    # Validate room_id if provided
    if item_data.room_id is not None:
        room = db.query(Room).filter(
            Room.id == item_data.room_id,
            Room.user_id == current_user.id
        ).first()
        if not room:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Room not found"
            )
    
    try:
        new_item = Item(
            **item_data.model_dump(),
            user_id=current_user.id
        )
        db.add(new_item)
        db.commit()
        db.refresh(new_item)
        return new_item
    except Exception as e:
        db.rollback()
        import traceback
        error_detail = f"Error: {str(e)}\nTraceback: {traceback.format_exc()}"
        print(error_detail)  # Log to console
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}"
        ) from e


@router.put("/{item_id}", response_model=ItemResponse)
def update_item(
    item_id: int,
    item_data: ItemUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    item = db.query(Item).filter(
        Item.id == item_id,
        Item.user_id == current_user.id
    ).first()
    
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Item not found"
        )
    
    update_data = item_data.model_dump(exclude_unset=True)
    
    if "category_id" in update_data and update_data["category_id"]:
        category = db.query(Category).filter(
            Category.id == update_data["category_id"],
            Category.user_id == current_user.id
        ).first()
        if not category:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Category not found"
            )
    
    try:
        for key, value in update_data.items():
            setattr(item, key, value)
        db.commit()
        db.refresh(item)
        return item
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        ) from e


@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_item(
    item_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    item = db.query(Item).filter(
        Item.id == item_id,
        Item.user_id == current_user.id
    ).first()
    
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Item not found"
        )
    
    db.delete(item)
    db.commit()
    
    return None
