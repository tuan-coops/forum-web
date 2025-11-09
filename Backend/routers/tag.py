from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from database import get_db
from models.tag import Tag
from models.forum_tag import ForumTag

router = APIRouter(
    prefix="/tag",
    tags=["Tag"]
)

@router.get("/top")
def get_top_tags(limit: int = 5, db: Session = Depends(get_db)):
    """
    Lấy ra top N tag được sử dụng nhiều nhất (mặc định 5)
    """
    results = (
        db.query(
            Tag.name,
            func.count(ForumTag.forum_id).label("usage_count")
        )
        .join(ForumTag, Tag.tag_id == ForumTag.tag_id)
        .group_by(Tag.tag_id)
        .order_by(func.count(ForumTag.forum_id).desc())
        .limit(limit)
        .all()
    )

    return [
        {"name": name, "count": count}
        for name, count in results
    ]
