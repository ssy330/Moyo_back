from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.message import Message
from app.models.user import User
from app.schemas.message import MessageOut

# ✅ api/v1까지 포함해서 prefix 지정
router = APIRouter(prefix="/api/v1/messages", tags=["Messages"])


@router.get("/rooms/{room_id}", response_model=list[MessageOut])
def get_messages(
    room_id: int,
    db: Session = Depends(get_db),
):
    # Message + User join
    stmt = (
        select(Message, User.nickname)
        .join(User, Message.user_id == User.id, isouter=True)
        .where(Message.room_id == room_id)
        .order_by(Message.created_at.asc())
        .limit(100)
    )
    rows = db.execute(stmt).all()

    result: list[MessageOut] = []
    for msg, nickname in rows:
        result.append(
            MessageOut(
                id=msg.id,
                room_id=msg.room_id,
                user_id=msg.user_id,
                content=msg.content,
                created_at=msg.created_at,
                user_nickname=nickname,
            )
        )
    return result