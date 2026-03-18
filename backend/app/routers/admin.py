from __future__ import annotations

from typing import List

from fastapi import APIRouter, Depends, Header, HTTPException
from sqlalchemy.orm import Session

from ..config import get_settings
from ..database import get_db
from ..models import Event
from ..schemas import EventCreate, EventRead, EventUpdate

router = APIRouter(prefix="/admin", tags=["admin"])


def require_admin(x_api_key: str | None = Header(default=None)) -> None:
    settings = get_settings()
    if x_api_key != settings.admin_api_key:
        raise HTTPException(status_code=401, detail="Unauthorized")


@router.post("/events", response_model=EventRead, dependencies=[Depends(require_admin)])
def create_event(event_in: EventCreate, db: Session = Depends(get_db)):
    event = Event(**event_in.model_dump())
    db.add(event)
    db.commit()
    db.refresh(event)
    return event


@router.patch(
    "/events/{event_id}",
    response_model=EventRead,
    dependencies=[Depends(require_admin)],
)
def update_event(event_id: int, event_in: EventUpdate, db: Session = Depends(get_db)):
    event = db.get(Event, event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")

    for field, value in event_in.model_dump(exclude_unset=True).items():
        setattr(event, field, value)

    db.add(event)
    db.commit()
    db.refresh(event)
    return event


@router.get(
    "/events",
    response_model=List[EventRead],
    dependencies=[Depends(require_admin)],
)
def list_all_events(db: Session = Depends(get_db)):
    events = db.query(Event).all()
    return events

