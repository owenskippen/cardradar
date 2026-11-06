"""Match a newly extracted show against events already in the database."""

from __future__ import annotations

from datetime import date
from typing import Optional

from rapidfuzz import fuzz
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..models import Event

NAME_THRESHOLD = 80
VENUE_THRESHOLD = 85


def find_duplicate(
    db: Session,
    name: str,
    show_date: Optional[date],
    city: Optional[str],
    venue: Optional[str],
) -> Optional[Event]:
    """Same show = same date and same city, plus a similar name or venue.

    Undated shows only match undated events in the same city with a very
    similar name, since there's little else to go on.
    """
    stmt = select(Event)
    if show_date:
        stmt = stmt.where(Event.date == show_date)
    else:
        stmt = stmt.where(Event.date.is_(None))
    if city:
        stmt = stmt.where(Event.city.ilike(city))

    best: tuple[float, Event] | None = None
    for event in db.scalars(stmt):
        name_score = fuzz.token_set_ratio(name.lower(), (event.name or "").lower())
        venue_score = (
            fuzz.token_set_ratio(venue.lower(), event.venue.lower())
            if venue and event.venue
            else 0
        )
        if show_date:
            is_match = name_score >= NAME_THRESHOLD or venue_score >= VENUE_THRESHOLD
        else:
            is_match = name_score >= 90
        score = max(name_score, venue_score)
        if is_match and (best is None or score > best[0]):
            best = (score, event)
    return best[1] if best else None
