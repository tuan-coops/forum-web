from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime

class User(Base):
    __tablename__ = "user"

    user_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    username = Column(String(50), nullable=False, unique=True)
    email = Column(String(100), nullable=False, unique=True)
    password_hash = Column(String(255), nullable=False)
    firebase_uid = Column(String(128), unique=True, nullable=True)  # 🆕 Thêm cột cho Firebase
    avatar = Column(String(255))
    background = Column(String(255))
    bio = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    forums_joined = relationship("Membership", back_populates="user", cascade="all, delete")
    posts = relationship("Post", back_populates="user", cascade="all, delete-orphan")
    messages = relationship("Message", back_populates="user")
    likes = relationship("Like", back_populates="user", cascade="all, delete")
