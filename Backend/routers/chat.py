from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from sqlalchemy.orm import Session
from database import get_db
from models.message import Message
from models.user import User
from datetime import datetime
from typing import Dict, List
import json
from datetime import datetime, timedelta, timezone

VN_TZ = timezone(timedelta(hours=7))  # Múi giờ Việt Nam (UTC+7)
router = APIRouter(prefix="/chat", tags=["Chat"])

# Lưu danh sách kết nối đang mở
active_connections: Dict[int, List[WebSocket]] = {}

@router.websocket("/ws/{forum_id}")
async def websocket_endpoint(websocket: WebSocket, forum_id: int, db: Session = Depends(get_db)):
    await websocket.accept()
    print(f"✅ WebSocket connected to forum {forum_id}")

    if forum_id not in active_connections:
        active_connections[forum_id] = []
    active_connections[forum_id].append(websocket)

    try:
        while True:
            data = await websocket.receive_text()
            print(f"💬 Message from forum {forum_id}: {data}")

            # Parse JSON từ frontend
            try:
                msg_data = json.loads(data)
                user = msg_data.get("user", "Ẩn danh")
                user_id = int(msg_data.get("user_id", 1))
                content = msg_data.get("content", "")
            except Exception as e:
                print("❌ Parse error:", e)
                continue

            # 🧩 Lưu xuống database
            new_msg = Message(
                forum_id=forum_id,
                user_id=user_id,
                content=content,
                created_at=datetime.now(VN_TZ)  # ✅ Giờ Việt Nam thật
            )
            db.add(new_msg)
            db.commit()
            db.refresh(new_msg)

            # 🛰️ Gửi lại cho toàn bộ client cùng forum
            payload = {
                "message_id": new_msg.message_id,
                "forum_id": forum_id,
                "user_id": user_id,
                "user": user,
                "content": content,
                "created_at": new_msg.created_at.isoformat()
            }
            for conn in active_connections[forum_id]:
                await conn.send_text(json.dumps(payload))

    except WebSocketDisconnect:
        print(f"🔌 Client disconnected from forum {forum_id}")
        if forum_id in active_connections:
            active_connections[forum_id].remove(websocket)

    except Exception as e:
        print(f"❌ Error in WebSocket forum {forum_id}: {e}")
        await websocket.close(code=403)

@router.get("/{forum_id}")
def get_messages(forum_id: int, db: Session = Depends(get_db)):
    messages = (
        db.query(Message, User.username)
        .join(User, User.user_id == Message.user_id)
        .filter(Message.forum_id == forum_id)
        .order_by(Message.created_at.asc())
        .all()
    )

    result = []
    for msg, username in messages:
        result.append({
            "message_id": msg.message_id,
            "forum_id": msg.forum_id,
            "user_id": msg.user_id,
            "username": username,
            "content": msg.content,
            "file_url": msg.file_url,
            "file_type": msg.file_type,
            "reply_to": msg.reply_to,
            "created_at": msg.created_at.isoformat()
        })
    return result
