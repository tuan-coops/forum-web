from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from database import Base

class User(Base):
    __tablename__ = "user"

    user_id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    avatar = Column(String(255))
    background = Column(String(255))
    bio = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Forum(Base):
    __tablename__ = "forum"

    forum_id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    tag = Column(String(50))
    avatar = Column(String(255))
    background = Column(String(255))
    created_by = Column(Integer, ForeignKey("user.user_id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    creator = relationship("User")
