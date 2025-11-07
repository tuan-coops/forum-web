from sqlalchemy import Column, Integer, Enum, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base
import enum

class RoleEnum(enum.Enum):
    member = "member"
    moderator = "moderator"
    admin = "admin"

class Membership(Base):
    __tablename__ = "membership"

    membership_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("user.user_id", ondelete="CASCADE"), nullable=False)
    forum_id = Column(Integer, ForeignKey("forum.forum_id", ondelete="CASCADE"), nullable=False)
    role = Column(Enum(RoleEnum), default=RoleEnum.member)
    joined_at = Column(DateTime, default=datetime.utcnow)

    # Liên kết ngược
    user = relationship("User", back_populates="forums_joined")
    forum = relationship("Forum", back_populates="members")
