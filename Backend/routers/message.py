from fastapi import APIRouter, Depends, HTTPException, Form, UploadFile, File, Request
from sqlalchemy.orm import Session
from database import get_db
from models.message import Message
from models.forum import Forum
from models.user import User
from datetime import datetime
import shutil, os
from typing import Optional

router = APIRouter(prefix="/message", tags=["Message"])

UPLOAD_DIR = "static/messages"
os.makedirs(UPLOAD_DIR, exist_ok=True)


# 🟢 Gửi message (có thể là text hoặc file)
@router.post("/send")
async def send_message(
    request: Request,
    forum_id: int = Form(...),
    user_id: int = Form(...),
    content: str = Form(""),
    reply_to: Optional[int] = Form(None),
    file: UploadFile = File(None),
    db: Session = Depends(get_db)
):
    # ⚙️ Fix lỗi ràng buộc khóa ngoại khi reply_to = 0 hoặc ""
    if reply_to in [0, "0", "", None]:
        reply_to = None

    file_url = None
    file_type = None

    # 🖼️ Xử lý file nếu có
    if file:
        filename = f"{datetime.now().timestamp()}_{file.filename}"
        file_path = os.path.join(UPLOAD_DIR, filename)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        base_url = str(request.base_url).rstrip("/")
        file_url = f"{base_url}/static/messages/{filename}"

        if file.content_type.startswith("image/"):
            file_type = "image"
        elif file.content_type.startswith("video/"):
            file_type = "video"
        else:
            file_type = "file"

    # 🧱 Tạo message mới
    new_msg = Message(
        forum_id=forum_id,
        user_id=user_id,
        content=content,
        file_url=file_url,
        file_type=file_type,
        reply_to=reply_to,  # Giờ an toàn vì không còn giá trị 0 hoặc ""
        created_at=datetime.utcnow()
    )
    db.add(new_msg)
    db.commit()
    db.refresh(new_msg)

    user = db.query(User).filter(User.user_id == user_id).first()

    # 🔁 Nếu là tin nhắn reply thì lấy preview
    reply_preview = None
    if reply_to:
        parent = db.query(Message).filter(Message.message_id == reply_to).first()
        if parent:
            reply_preview = {
                "id": parent.message_id,
                "username": db.query(User.username).filter(User.user_id == parent.user_id).scalar(),
                "content": parent.content
            }

    # ✅ Trả kết quả
    return {
        "message_id": new_msg.message_id,
        "forum_id": forum_id,
        "user_id": user_id,
        "username": user.username if user else "Unknown",
        "content": new_msg.content,
        "file_url": new_msg.file_url,
        "file_type": new_msg.file_type,
        "reply_to": new_msg.reply_to,
        "reply_preview": reply_preview,
        "created_at": new_msg.created_at
    }

# 🟣 Lấy danh sách message của 1 forum
@router.get("/forum/{forum_id}")
def get_messages(request: Request, forum_id: int, db: Session = Depends(get_db)):
    base_url = str(request.base_url).rstrip("/")

    messages = (
        db.query(Message, User.username)
        .join(User, Message.user_id == User.user_id)
        .filter(Message.forum_id == forum_id)
        .order_by(Message.created_at.asc())
        .all()
    )

    result = []
    for m in messages:
        msg = m.Message
        reply_preview = None
        if msg.reply_to:
            parent = (
                db.query(Message, User.username)
                .join(User, Message.user_id == User.user_id)
                .filter(Message.message_id == msg.reply_to)
                .first()
            )
            if parent:
                reply_preview = {
                    "id": parent.Message.message_id,
                    "username": parent.username,
                    "content": parent.Message.content[:100]
                    + ("..." if len(parent.Message.content) > 100 else "")
                }

        result.append({
            "message_id": msg.message_id,
            "user_id": msg.user_id,
            "username": m.username,
            "content": msg.content,
            "file_url": msg.file_url,
            "file_type": msg.file_type,
            "reply_to": msg.reply_to,
            "reply_preview": reply_preview,
            "created_at": msg.created_at
        })

    return result
