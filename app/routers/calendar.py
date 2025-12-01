from datetime import datetime
from typing import List
from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import select, and_, or_

from app.database import get_db
from app.schemas.calendar import EventOut, EventCreate, EventUpdate
from app.services import calendar_service
from app.models import CalendarEvent
from app.services.group_service import get_my_group_ids

from app.deps.auth import current_user 
from app.models.user import User
from app.deps.auth import current_user as get_current_user

router = APIRouter(
    prefix="/calendar",        # 최종 주소: /api/v1/calendar/...
    tags=["calendar"],
)

@router.get("/events", response_model=List[EventOut])
def list_events(
    from_: datetime = Query(..., alias="from"),   # ← 수정
    to: datetime = Query(...),  # ← 타입 명시 + Query 사용
    scope: Literal["all", "personal", "group"] = "all",
    group_id: int | None = None,
    db: Session = Depends(get_db),
    current_user: User =Depends(get_current_user),
):
    user_id = current_user.id
    
    q = select(CalendarEvent).where(
        CalendarEvent.start_at < to,
        CalendarEvent.end_at >= from_,
    )

    if scope == "personal":
        q = q.where(
            CalendarEvent.user_id == user_id,
            CalendarEvent.group_id.is_(None),
        )

    elif scope == "group":
        if group_id is None:
            raise HTTPException(400, "group_id is required when scope=group")
        # (여기서 user가 해당 group 멤버인지 체크)
        q = q.where(CalendarEvent.group_id == group_id)

    elif scope == "all":
        # 내가 속한 그룹 id 목록 가져오기 (service 함수 사용)
        my_group_ids = get_my_group_ids(db, user_id)
        q = q.where(
            or_(
                and_(
                    CalendarEvent.user_id == user_id,
                    CalendarEvent.group_id.is_(None),
                ),
                # 내가 속한 그룹들의 일정
                CalendarEvent.group_id.in_(my_group_ids),
            )
        )
        
    events = calendar_service.get_events_between(
        db=db,
        user_id=current_user.id,
        start=from_,
        end=to,
    )
    return events

@router.post("/events", response_model=EventOut, status_code=status.HTTP_201_CREATED)
def create_event(
    data: EventCreate,
    db: Session = Depends(get_db),
    current_user=Depends(current_user),
):
    if data.start_at >= data.end_at:
        raise HTTPException(status_code=400, detail="start_at must be before end_at")

    event = calendar_service.create_event(
        db=db,
        user_id=current_user.id,
        data=data,
    )
    return event

@router.patch("/events/{event_id}", response_model=EventOut)
def update_event(
    event_id: int,
    data: EventUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(current_user),
):
    event = calendar_service.update_event(
        db=db,
        user_id=current_user.id,
        event_id=event_id,
        data=data,
    )
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    return event

@router.delete("/events/{event_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_event(
    event_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(current_user),
):
    ok = calendar_service.delete_event(
        db=db,
        user_id=current_user.id,
        event_id=event_id,
    )
    if not ok:
        raise HTTPException(status_code=404, detail="Event not found")
    return