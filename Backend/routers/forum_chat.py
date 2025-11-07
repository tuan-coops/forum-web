from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import json
from datetime import datetime

router = APIRouter(prefix="/chat", tags=["Chat"])

active_forums = {}

@router.websocket("/ws/{forum_id}")
async def chat_ws(websocket: WebSocket, forum_id: int):
    await websocket.accept()
    if forum_id not in active_forums:
        active_forums[forum_id] = []
    active_forums[forum_id].append(websocket)
    print(f"✅ Kết nối mới vào forum {forum_id}")

    try:
        while True:
            data = await websocket.receive_text()
            payload = json.loads(data)
            for conn in active_forums[forum_id]:
                await conn.send_text(json.dumps({
                    "user": payload["user"],
                    "content": payload["content"],
                    "created_at": datetime.utcnow().isoformat()
                }))
    except WebSocketDisconnect:
        active_forums[forum_id].remove(websocket)
        print(f"❌ Người dùng rời khỏi forum {forum_id}")
