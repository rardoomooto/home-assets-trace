from datetime import date
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.database import get_db
from app.models import User, Item, Category, Room, Family, FamilyMember
from app.schemas import ItemCreate, ItemUpdate, ItemResponse, ItemListResponse
from app.auth import get_current_user

router = APIRouter(prefix="/api/items", tags=["items"])


def get_family_ids_for_user(user_id: int, db: Session) -> list[int]:
    """获取用户所属的所有家庭 ID 列表"""
    memberships = db.query(FamilyMember.family_id).filter(
        FamilyMember.user_id == user_id
    ).all()
    return [m[0] for m in memberships]


@router.get("", response_model=ItemListResponse)
def get_items(
    name: Optional[str] = Query(None, description="Filter by item name"),
    category_id: Optional[int] = Query(None, description="Filter by category ID"),
    room_id: Optional[int] = Query(None, description="Filter by room ID"),
    family_id: Optional[int] = Query(None, description="Filter by family ID"),
    expired: Optional[bool] = Query(None, description="Filter expired items"),
    expiring_soon: Optional[bool] = Query(None, description="Filter items expiring within 30 days"),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # 获取用户所属的家庭 ID 列表
    user_family_ids = get_family_ids_for_user(current_user.id, db)
    
    # 查询逻辑：
    # 1. 自己的物品（无论是否私有）
    # 2. 同家庭成员的非私有物品
    query = db.query(Item).filter(
        or_(
            Item.user_id == current_user.id,  # 自己的物品
            (Item.family_id.in_(user_family_ids)) & (Item.is_private == False)  # 同家庭非私有物品
        )
    )
    
    if name:
        query = query.filter(Item.name.ilike(f"%{name}%"))
    
    if category_id:
        query = query.filter(Item.category_id == category_id)
    
    if room_id:
        query = query.filter(Item.room_id == room_id)
    
    if family_id:
        query = query.filter(Item.family_id == family_id)
    
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
    # 确保用户有默认家庭
    if not item_data.family_id:
        from app.routers.family import get_or_create_default_family
        default_family = get_or_create_default_family(current_user, db)
        item_data.family_id = default_family.id
    
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
