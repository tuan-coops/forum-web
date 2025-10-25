from pydantic import BaseModel
from typing import Optional

class ForumCreate(BaseModel):
    name: str
    description: Optional[str] = None
    tag: Optional[str] = None
    avatar: Optional[str] = None
    background: Optional[str] = None
    created_by: int

class ForumResponse(BaseModel):
    forum_id: int
    name: str
    description: Optional[str]
    tag: Optional[str]
    avatar: Optional[str]
    background: Optional[str]
    created_by: int

    class Config:
        orm_mode = True
