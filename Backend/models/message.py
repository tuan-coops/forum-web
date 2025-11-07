from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base

class Message(Base):
    __tablename__ = "message"

    message_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    forum_id = Column(Integer, ForeignKey("forum.forum_id", ondelete="CASCADE"), nullable=False)
    user_id = Column(Integer, ForeignKey("user.user_id", ondelete="CASCADE"), nullable=False)
    content = Column(Text, nullable=True)
    file_url = Column(String(255), nullable=True)
    file_type = Column(String(50), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # ✅ Cho phép reply_to NULL, không lỗi nếu message cha bị xóa
    reply_to = Column(Integer, ForeignKey("message.message_id", ondelete="SET NULL"), nullable=True)

    # Quan hệ với Forum và User
    forum = relationship("Forum", back_populates="messages")
    user = relationship("User", back_populates="messages")

    # Quan hệ đệ quy: message có thể reply một message khác
    parent = relationship("Message", remote_side=[message_id], backref="replies")
