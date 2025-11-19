from sqlalchemy.orm import Session
from datetime import datetime
from typing import List, Optional

from app.models.calendar import UserEvent
from app.schemas.calendar import EventCreate, EventUpdate

def get_events_between(
    db: Session,
    user_id: int,
    start: datetime,
    end: datetime,
) -> List[UserEvent]:
    return (
        db.query(UserEvent)
        .filter(
            UserEvent.user_id == user_id,
            UserEvent.start_at < end,
            UserEvent.end_at >= start,
        )
        .all()
    )

def create_event(db: Session, user_id: int, data: EventCreate) -> UserEvent:
    event = UserEvent(
        user_id=user_id,
        title=data.title,
        description=data.description,
        start_at=data.start_at,
        end_at=data.end_at,
        all_day=data.all_day,
    )
    db.add(event)
    db.commit()
    db.refresh(event)
    return event

def update_event(
    db: Session,
    user_id: int,
    event_id: int,
    data: EventUpdate,
) -> Optional[UserEvent]:
    event = (
        db.query(UserEvent)
        .filter(UserEvent.id == event_id, UserEvent.user_id == user_id)
        .first()
    )
    if not event:
        return None

    for field, value in data.dict(exclude_unset=True).items():
        setattr(event, field, value)

    db.commit()
    db.refresh(event)
    return event

def delete_event(db: Session, user_id: int, event_id: int) -> bool:
    event = (
        db.query(UserEvent)
        .filter(UserEvent.id == event_id, UserEvent.user_id == user_id)
        .first()
    )
    if not event:
        return False

    db.delete(event)
    db.commit()
    return True