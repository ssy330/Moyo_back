# app/routers/rooms.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.group import Group
from app.models.room import ChatRoom, RoomMember
from app.models.user import User
from app.deps.auth import current_user
from app.schemas.room import RoomCreate, RoomOut

# ✅ api/v1까지 포함
router = APIRouter(prefix="/api/v1/rooms", tags=["Rooms"])


@router.get("/", response_model=list[RoomOut])
def list_rooms(db: Session = Depends(get_db)):
    rooms = db.query(ChatRoom).all()
    return rooms


# 🔥 누구나 방 만들 수 있게 user 의존성 제거
@router.post("/", response_model=RoomOut, status_code=status.HTTP_201_CREATED)
def create_room(
    data: RoomCreate,
    db: Session = Depends(get_db),
):
    room = ChatRoom(name=data.name)
    db.add(room)
    db.commit()
    db.refresh(room)
    return room


# join은 나중에 로그인 붙이고 쓸 때
@router.post("/{room_id}/join", status_code=status.HTTP_204_NO_CONTENT)
def join_room(
    room_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(current_user),
):
    exists = db.query(ChatRoom).filter_by(id=room_id).first()
    if not exists:
        raise HTTPException(status_code=404, detail="방이 존재하지 않습니다.")

    already = (
        db.query(RoomMember)
        .filter_by(room_id=room_id, user_id=user.id)
        .first()
    )

    if not already:
        db.add(RoomMember(room_id=room_id, user_id=user.id))
        db.commit()


# ✅✅ 그룹 전용 채팅방: group_id 기준으로 1개 자동 생성/조회
@router.post("/by-group/{group_id}", response_model=RoomOut)
def get_or_create_group_room(
    group_id: int,
    db: Session = Depends(get_db),
):
    # 1) 그룹 존재 여부 확인
    group = db.query(Group).filter_by(id=group_id).first()
    if not group:
        raise HTTPException(status_code=404, detail="그룹이 존재하지 않습니다.")

    # 2) 기존에 이 그룹용 방이 있으면 그대로 리턴
    room = db.query(ChatRoom).filter_by(group_id=group_id).first()
    if room:
        return room

    # 3) 없으면 새로 만드는 로직
    room = ChatRoom(
        name=f"{group.name} 채팅방",
        group_id=group_id,
    )
    db.add(room)
    db.commit()
    db.refresh(room)
    return room