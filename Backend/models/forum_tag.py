from sqlalchemy import Column, Integer, ForeignKey
from database import Base
from sqlalchemy.orm import relationship

class ForumTag(Base):
    __tablename__ = "forum_tag"

    forum_id = Column(Integer, ForeignKey("forum.forum_id", ondelete="CASCADE"), primary_key=True)
    tag_id = Column(Integer, ForeignKey("tags.tag_id", ondelete="CASCADE"), primary_key=True)

    forum = relationship("Forum", back_populates="forum_tags")
    tag = relationship("Tag", back_populates="forum_tags")
