from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from enum import Enum


class ForumCreate(BaseModel):
    name: str
    caption: Optional[str] = None
    tag: Optional[str] = None
    background: Optional[str] = None
    created_by: Optional[int] = None

class ForumResponse(BaseModel):
    forum_id: int
    name: str
    caption: Optional[str]
    tag: Optional[str]
    background: Optional[str]
    created_by: int

    class Config:
        orm_mode = True
        
class SignupRequest(BaseModel):
    username: str
    email: str
    password: str
    avatar: Optional[str] = None
    background: Optional[str] = None
    bio: Optional[str] = None

class SigninRequest(BaseModel):
    username: str
    password: str

class RoleEnum(str, Enum):
    member = "member"
    moderator = "moderator"
    admin = "admin"

class MembershipBase(BaseModel):
    user_id: int
    forum_id: int
    role: Optional[RoleEnum] = RoleEnum.member

class MembershipResponse(MembershipBase):
    membership_id: int
    joined_at: datetime

    class Config:
        orm_mode = True
class GoogleRegisterRequest(BaseModel):
    email: str
    firebase_uid: str
    username: str
    password: str
    avatar: str | None = None
    bio: str | None = None
