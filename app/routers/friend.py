# app/routers/friend.py
from fastapi import APIRouter, Depends, HTTPException, status,Path
from sqlalchemy import func
from sqlalchemy.orm import Session, joinedload

from app.deps.auth import current_user as get_current_user 
from app.database import get_db
from app.models.user import User
from app.models.friend_request import FriendRequest
from app.schemas.friend import FriendOut, FriendRequestCreate, FriendRequestOut


router = APIRouter(
    prefix="/friend-requests",
    tags=["friends"],
)

@router.post("", response_model=FriendRequestOut)
def send_friend_request(
    payload: FriendRequestCreate,
    db: Session = Depends(get_db),
    me: User = Depends(get_current_user),
):
    if payload.receiver_id == me.id:
        raise HTTPException(400, detail="자기 자신에게는 친구 요청을 보낼 수 없습니다.")

    # 최근 요청 1개 가져오기
    existing = (
        db.query(FriendRequest)
        .filter(
            FriendRequest.requester_id == me.id,
            FriendRequest.receiver_id == payload.receiver_id,
        )
        .order_by(FriendRequest.id.desc())
        .first()
    )

    # 1) 이미 친구인 경우 막기
    if existing and existing.status == "ACCEPTED":
        raise HTTPException(400, detail="이미 친구입니다.")

    # 2) 아직 PENDING인 요청이 있으면, 그냥 재발송 느낌만 내고 새로 안 만듦
    if existing and existing.status == "PENDING":
        # 원하면 created_at만 최신으로 갱신해도 됨
        existing.created_at = func.now()
        existing.group_id = payload.group_id
        db.commit()
        db.refresh(existing)
        return existing

    # 3) REJECTED / CANCELED 였으면 다시 PENDING으로 되살리기 (재요청)
    if existing and existing.status in ("REJECTED", "CANCELED"):
        existing.status = "PENDING"
        existing.group_id = payload.group_id
        existing.created_at = func.now()
        db.commit()
        db.refresh(existing)
        return existing

    # 4) 그 외엔 새 요청 생성
    fr = FriendRequest(
        requester_id=me.id,
        receiver_id=payload.receiver_id,
        group_id=payload.group_id,
        status="PENDING",
    )
    db.add(fr)
    db.commit()
    db.refresh(fr)
    return fr

# 친구 요청 목록
@router.get("/incoming", response_model=list[FriendRequestOut])
def get_incoming_friend_requests(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    qs = (
        db.query(FriendRequest)
        .options(
            joinedload(FriendRequest.requester),  # 요청 보낸 사람 join
            joinedload(FriendRequest.group),      # 🔥 그룹 join
        )
        .filter(
            FriendRequest.receiver_id == current_user.id,
            FriendRequest.status == "PENDING",
        )
        .order_by(FriendRequest.created_at.desc())
        .all()
    )
    return qs


@router.post("/{request_id}/accept", response_model=FriendRequestOut)
def accept_friend_request(
    request_id: int = Path(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    fr = db.query(FriendRequest).filter(FriendRequest.id == request_id).first()
    if not fr:
        raise HTTPException(status_code=404, detail="요청을 찾을 수 없습니다.")

    if fr.receiver_id != current_user.id:
        raise HTTPException(status_code=403, detail="권한이 없습니다.")

    if fr.status != "PENDING":
        raise HTTPException(status_code=400, detail="이미 처리된 요청입니다.")

    fr.status = "ACCEPTED"
    db.commit()
    db.refresh(fr)
    return fr

# 수락 거절
@router.post("/{request_id}/reject", response_model=FriendRequestOut)
def reject_friend_request(
    request_id: int = Path(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    fr = db.query(FriendRequest).filter(FriendRequest.id == request_id).first()
    if not fr:
        raise HTTPException(status_code=404, detail="요청을 찾을 수 없습니다.")

    if fr.receiver_id != current_user.id:
        raise HTTPException(status_code=403, detail="권한이 없습니다.")

    if fr.status != "PENDING":
        raise HTTPException(status_code=400, detail="이미 처리된 요청입니다.")

    fr.status = "REJECTED"
    db.commit()
    db.refresh(fr)
    return fr

# 친구 목록 리스트
@router.get("/friends", response_model=list[FriendOut])
def list_my_friends(
    db: Session = Depends(get_db),
    me: User = Depends(get_current_user),
):
    # 내가 요청자였던 경우 (A → B, ACCEPTED)
    sent = (
        db.query(FriendRequest)
        .options(
            joinedload(FriendRequest.receiver),
            joinedload(FriendRequest.group),
        )
        .filter(
            FriendRequest.requester_id == me.id,
            FriendRequest.status == "ACCEPTED",
        )
        .all()
    )

    # 내가 받은 사람이었던 경우 (B ← A, ACCEPTED)
    received = (
        db.query(FriendRequest)
        .options(
            joinedload(FriendRequest.requester),
            joinedload(FriendRequest.group),
        )
        .filter(
            FriendRequest.receiver_id == me.id,
            FriendRequest.status == "ACCEPTED",
        )
        .all()
    )

    results: list[FriendOut] = []

    # A → B: friend = receiver
    for fr in sent:
        friend_user = fr.receiver
        results.append(
            FriendOut(
                id=fr.id,
                created_at=fr.created_at,
                friend=friend_user,
                group=fr.group,
            )
        )

    # B ← A: friend = requester
    for fr in received:
        friend_user = fr.requester
        results.append(
            FriendOut(
                id=fr.id,
                created_at=fr.created_at,
                friend=friend_user,
                group=fr.group,
            )
        )

    return results