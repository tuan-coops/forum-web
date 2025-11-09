from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from database import Base

class Tag(Base):
    __tablename__ = "tags"

    tag_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(50), unique=True, nullable=False)

    # 🧩 Quan hệ hai chiều với ForumTag
    forum_tags = relationship("ForumTag", back_populates="tag", cascade="all, delete")
