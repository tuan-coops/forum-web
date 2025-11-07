from sqlalchemy import Column, Integer, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base

class Like(Base):
    __tablename__ = "like"

    like_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("user.user_id", ondelete="CASCADE"), nullable=False)
    forum_id = Column(Integer, ForeignKey("forum.forum_id", ondelete="CASCADE"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Liên kết ngược
    user = relationship("User", back_populates="likes")
    forum = relationship("Forum", back_populates="likes")
