# app/deps/auth_ws.py
from fastapi import WebSocket, WebSocketException, status, Depends
from sqlalchemy.orm import Session
import jwt  # PyJWT

from app.database import get_db
from app.models.user import User
from app.utils.security import decode_access_token  # 네가 만든 util

async def get_current_user_ws(
    websocket: WebSocket,
    db: Session = Depends(get_db),
) -> User:
    # 1) 쿼리스트링에서 token=? 읽기
    token = websocket.query_params.get("token")
    if not token:
        raise WebSocketException(code=status.WS_1008_POLICY_VIOLATION)

    # 2) 토큰 디코드
    try:
        payload = decode_access_token(token)
    except jwt.PyJWTError:
        # 토큰이 유효하지 않으면 WebSocket 정책 위반 코드로 끊기
        raise WebSocketException(code=status.WS_1008_POLICY_VIOLATION)

    # 👉 로그인 때 create_access_token({"sub": user.email}) 썼으니까
    email = payload.get("sub")
    if not email:
        raise WebSocketException(code=status.WS_1008_POLICY_VIOLATION)

    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise WebSocketException(code=status.WS_1008_POLICY_VIOLATION)

    return user
