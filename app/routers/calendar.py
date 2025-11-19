from datetime import datetime
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.calendar import EventOut, EventCreate, EventUpdate
from app.services import calendar_service

from app.deps.auth import current_user 

router = APIRouter(
    prefix="/calendar",        # 최종 주소: /api/v1/calendar/...
    tags=["calendar"],
)

@router.get("/events", response_model=List[EventOut])
def list_events(
    from_: datetime,
    to: datetime,
    db: Session = Depends(get_db),
    current_user=Depends(current_user),
):
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