# app/websocket/endpoints.py
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from sqlalchemy.orm import Session

from app.websocket.manager import manager
from app.database import get_db
from app.models.message import Message
from app.models.user import User
from app.deps.auth_ws import get_current_user_ws  # 🔥 추가

router = APIRouter()

@router.websocket("/ws/rooms/{room_id}")
async def websocket_room(
    websocket: WebSocket,
    room_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user_ws),  # 🔥 로그인 유저 주입
):
    await manager.connect(room_id, websocket)

    try:
        while True:
            data = await websocket.receive_json()
            content = data.get("content")

            if not content:
                continue

            # 🔹 이제 user_id를 실제 유저로 세팅
            msg = Message(
                room_id=room_id,
                user_id=user.id,
                content=content,
            )
            db.add(msg)
            db.commit()
            db.refresh(msg)

            payload = {
                "id": msg.id,
                "room_id": room_id,
                "user_id": user.id,
                "nickname": user.nickname,  # DB에 있는 닉네임 사용
                "content": msg.content,
                "created_at": msg.created_at.isoformat(),
            }

            await manager.broadcast(room_id, payload)

    except WebSocketDisconnect:
        manager.disconnect(room_id, websocket)
    except Exception as e:
        print(f"[WS] ERROR in room {room_id}: {e}")
        manager.disconnect(room_id, websocket)
        try:
            await websocket.close(code=1011)
        except Exception:
            pass
