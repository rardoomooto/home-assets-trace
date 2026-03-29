from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload

from app.database import get_db
from app.models import User, Family, FamilyMember
from app.schemas import (
    FamilyCreate, FamilyUpdate, FamilyResponse, FamilyListResponse,
    AddMemberRequest, FamilyMemberResponse
)
from app.auth import get_current_user

router = APIRouter(prefix="/api/families", tags=["families"])


def get_user_families(user_id: int, db: Session) -> list[Family]:
    """获取用户所属的所有家庭"""
    memberships = db.query(FamilyMember).filter(
        FamilyMember.user_id == user_id
    ).options(joinedload(FamilyMember.family).joinedload(Family.members)).all()
    return [m.family for m in memberships]


def get_or_create_default_family(user: User, db: Session) -> Family:
    """获取或创建用户的默认家庭"""
    # 查找用户的默认家庭
    membership = db.query(FamilyMember).filter(
        FamilyMember.user_id == user.id
    ).options(joinedload(FamilyMember.family)).first()
    
    if membership:
        return membership.family
    
    # 创建默认家庭
    default_family = Family(
        name=f"{user.username}的家庭",
        is_default=True
    )
    db.add(default_family)
    db.commit()
    db.refresh(default_family)
    
    # 添加用户为成员
    member = FamilyMember(
        family_id=default_family.id,
        user_id=user.id,
        role="owner"
    )
    db.add(member)
    db.commit()
    
    return default_family


def build_family_response(family: Family) -> dict:
    """构建家庭响应数据"""
    response_data = {
        "id": family.id,
        "name": family.name,
        "is_default": family.is_default,
        "created_at": family.created_at,
        "members": []
    }
    
    for member in family.members:
        response_data["members"].append({
            "id": member.id,
            "user_id": member.user_id,
            "username": member.user.username,
            "role": member.role,
            "joined_at": member.joined_at
        })
    
    return response_data


@router.get("", response_model=FamilyListResponse)
def get_families(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取用户所属的所有家庭"""
    families = get_user_families(current_user.id, db)
    # 手动构建响应
    family_responses = []
    for family in families:
        family_responses.append(build_family_response(family))
    return {"families": family_responses}


@router.post("", response_model=FamilyResponse, status_code=status.HTTP_201_CREATED)
def create_family(
    family_data: FamilyCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """创建新家庭"""
    new_family = Family(
        name=family_data.name,
        is_default=False
    )
    db.add(new_family)
    db.commit()
    db.refresh(new_family)
    
    # 创建者作为所有者加入
    member = FamilyMember(
        family_id=new_family.id,
        user_id=current_user.id,
        role="owner"
    )
    db.add(member)
    db.commit()
    
    # 重新查询家庭，包含成员和用户信息
    family_with_members = db.query(Family).options(
        joinedload(Family.members).joinedload(FamilyMember.user)
    ).filter(Family.id == new_family.id).first()
    
    # 手动构建响应，确保包含 username 字段
    response_data = {
        "id": family_with_members.id,
        "name": family_with_members.name,
        "is_default": family_with_members.is_default,
        "created_at": family_with_members.created_at,
        "members": []
    }
    
    for member in family_with_members.members:
        response_data["members"].append({
            "id": member.id,
            "user_id": member.user_id,
            "username": member.user.username,
            "role": member.role,
            "joined_at": member.joined_at
        })
    
    return response_data


@router.get("/{family_id}", response_model=FamilyResponse)
def get_family(
    family_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取家庭详情"""
    membership = db.query(FamilyMember).filter(
        FamilyMember.family_id == family_id,
        FamilyMember.user_id == current_user.id
    ).first()
    
    if not membership:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Family not found or you are not a member"
        )
    
    family = db.query(Family).options(
        joinedload(Family.members).joinedload(FamilyMember.user)
    ).filter(Family.id == family_id).first()
    
    return build_family_response(family)


@router.put("/{family_id}", response_model=FamilyResponse)
def update_family(
    family_id: int,
    family_data: FamilyUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """更新家庭信息（仅管理员/所有者）"""
    membership = db.query(FamilyMember).filter(
        FamilyMember.family_id == family_id,
        FamilyMember.user_id == current_user.id,
        FamilyMember.role.in_(["owner", "admin"])
    ).first()
    
    if not membership:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only owner or admin can update family"
        )
    
    family = db.query(Family).filter(Family.id == family_id).first()
    if not family:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Family not found"
        )
    
    if family_data.name:
        family.name = family_data.name
    
    db.commit()
    db.refresh(family)
    
    # 重新查询包含成员信息的家庭
    family_with_members = db.query(Family).options(
        joinedload(Family.members).joinedload(FamilyMember.user)
    ).filter(Family.id == family_id).first()
    
    return build_family_response(family_with_members)


@router.delete("/{family_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_family(
    family_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """删除家庭（仅所有者，不能删除默认家庭）"""
    membership = db.query(FamilyMember).filter(
        FamilyMember.family_id == family_id,
        FamilyMember.user_id == current_user.id,
        FamilyMember.role == "owner"
    ).first()
    
    if not membership:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only owner can delete family"
        )
    
    family = db.query(Family).filter(Family.id == family_id).first()
    if not family:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Family not found"
        )
    
    if family.is_default:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete default family"
        )
    
    # 删除所有成员关系
    db.query(FamilyMember).filter(FamilyMember.family_id == family_id).delete()
    db.delete(family)
    db.commit()


@router.post("/{family_id}/members", response_model=FamilyMemberResponse)
def add_member(
    family_id: int,
    member_data: AddMemberRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """添加家庭成员（仅管理员/所有者）"""
    membership = db.query(FamilyMember).filter(
        FamilyMember.family_id == family_id,
        FamilyMember.user_id == current_user.id,
        FamilyMember.role.in_(["owner", "admin"])
    ).first()
    
    if not membership:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only owner or admin can add members"
        )
    
    # 查找要添加的用户
    user_to_add = db.query(User).filter(User.username == member_data.username).first()
    if not user_to_add:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # 检查是否已经是成员
    existing_member = db.query(FamilyMember).filter(
        FamilyMember.family_id == family_id,
        FamilyMember.user_id == user_to_add.id
    ).first()
    
    if existing_member:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User is already a member"
        )
    
    new_member = FamilyMember(
        family_id=family_id,
        user_id=user_to_add.id,
        role=member_data.role
    )
    db.add(new_member)
    db.commit()
    db.refresh(new_member)
    
    return {
        "id": new_member.id,
        "user_id": user_to_add.id,
        "username": user_to_add.username,
        "role": new_member.role,
        "joined_at": new_member.joined_at
    }


@router.delete("/{family_id}/members/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_member(
    family_id: int,
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """移除家庭成员"""
    # 只有自己可以退出，或管理员/所有者可以移除其他人
    membership = db.query(FamilyMember).filter(
        FamilyMember.family_id == family_id,
        FamilyMember.user_id == current_user.id
    ).first()
    
    if not membership:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not a member of this family"
        )
    
    target_membership = db.query(FamilyMember).filter(
        FamilyMember.family_id == family_id,
        FamilyMember.user_id == user_id
    ).first()
    
    if not target_membership:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Member not found"
        )
    
    # 检查权限
    is_self = user_id == current_user.id
    is_admin = membership.role in ["owner", "admin"]
    
    if not is_self and not is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admin can remove other members"
        )
    
    # 所有者不能被移除（除非自己退出且有其他管理员）
    if target_membership.role == "owner" and not is_self:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot remove owner from family"
        )
    
    db.delete(target_membership)
    db.commit()
