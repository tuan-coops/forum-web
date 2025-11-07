from sqlalchemy import Column, Integer, String, Text, DateTime
from database import Base
from datetime import datetime
from sqlalchemy.orm import relationship

class Forum(Base):
    __tablename__ = "forum"

    forum_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    caption = Column(Text)
    tag = Column(String(50))
    background = Column(String(255), default="/Backend/static/source/default-background.jpg")  # ✅ đúng cú pháp
    created_by = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)

    members = relationship("Membership", back_populates="forum", cascade="all, delete")
    messages = relationship("Message", back_populates="forum")
    likes = relationship("Like", back_populates="forum", cascade="all, delete")