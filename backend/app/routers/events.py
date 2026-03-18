from __future__ import annotations

from datetime import date
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import and_, select
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Event
from ..schemas import EventRead, EventMapPoint

router = APIRouter(prefix="/events", tags=["events"])


@router.get("", response_model=List[EventRead])
def list_events(
    city: Optional[str] = Query(default=None),
    start_date: Optional[date] = Query(default=None),
    end_date: Optional[date] = Query(default=None),
    tags: Optional[str] = Query(
        default=None,
        description="Comma-separated list of tags to filter by",
    ),
    search: Optional[str] = Query(default=None),
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
):
    stmt = select(Event).where(Event.is_hidden.is_(False))

    if city:
        stmt = stmt.where(Event.city.ilike(f"%{city}%"))

    if start_date:
        stmt = stmt.where(Event.date >= start_date)
    if end_date:
        stmt = stmt.where(Event.date <= end_date)

    if tags:
        tag_list = [t.strip().lower() for t in tags.split(",") if t.strip()]
        if tag_list:
            stmt = stmt.where(
                and_(
                    *[Event.tags.any(tag) for tag in tag_list],  # type: ignore[arg-type]
                )
            )

    if search:
        pattern = f"%{search}%"
        stmt = stmt.where(Event.name.ilike(pattern) | Event.description.ilike(pattern))

    stmt = stmt.order_by(Event.date, Event.start_time).limit(limit).offset(offset)
    events = db.scalars(stmt).unique().all()
    return events


@router.get("/{event_id}", response_model=EventRead)
def get_event(event_id: int, db: Session = Depends(get_db)):
    event = db.get(Event, event_id)
    if not event or event.is_hidden:
        raise HTTPException(status_code=404, detail="Event not found")
    return event


@router.get("/map", response_model=List[EventMapPoint])
def get_event_map_points(
    city: Optional[str] = Query(default=None),
    start_date: Optional[date] = Query(default=None),
    end_date: Optional[date] = Query(default=None),
    db: Session = Depends(get_db),
):
    stmt = select(Event).where(
        Event.is_hidden.is_(False),
        Event.lat.is_not(None),
        Event.lng.is_not(None),
    )

    if city:
        stmt = stmt.where(Event.city.ilike(f"%{city}%"))
    if start_date:
        stmt = stmt.where(Event.date >= start_date)
    if end_date:
        stmt = stmt.where(Event.date <= end_date)

    events = db.scalars(stmt).unique().all()

    return [
        EventMapPoint(
            id=e.id,
            name=e.name,
            date=e.date,
            city=e.city,
            lat=e.lat or 0.0,
            lng=e.lng or 0.0,
            tags=e.tags or [],
        )
        for e in events
    ]

