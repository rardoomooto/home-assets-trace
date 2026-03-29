from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class FamilyBase(BaseModel):
    name: str


class FamilyCreate(FamilyBase):
    pass


class FamilyUpdate(FamilyBase):
    name: Optional[str] = None


class FamilyMemberResponse(BaseModel):
    id: int
    user_id: int
    username: str
    role: str
    joined_at: datetime

    class Config:
        from_attributes = True


class FamilyResponse(FamilyBase):
    id: int
    is_default: bool
    created_at: datetime
    members: list[FamilyMemberResponse] = []

    class Config:
        from_attributes = True


class FamilyListResponse(BaseModel):
    families: list[FamilyResponse]


class AddMemberRequest(BaseModel):
    username: str
    role: str = "member"  # admin, member
