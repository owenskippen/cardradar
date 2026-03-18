from __future__ import annotations

from datetime import date, time, datetime
from typing import Optional

from sqlalchemy import (
    Boolean,
    Column,
    Date,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import ARRAY, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .database import Base


class Event(Base):
    __tablename__ = "events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    date: Mapped[Optional[date]] = mapped_column(Date, index=True)
    start_time: Mapped[Optional[time]] = mapped_column()
    end_time: Mapped[Optional[time]] = mapped_column()
    venue: Mapped[Optional[str]] = mapped_column(String(255))
    address: Mapped[Optional[str]] = mapped_column(String(255))
    city: Mapped[Optional[str]] = mapped_column(String(100), index=True)
    province: Mapped[str] = mapped_column(String(10), default="BC")
    postal_code: Mapped[Optional[str]] = mapped_column(String(20))
    organizer: Mapped[Optional[str]] = mapped_column(String(255))
    website_url: Mapped[Optional[str]] = mapped_column(String(500))
    source_url_primary: Mapped[Optional[str]] = mapped_column(String(500))
    description: Mapped[Optional[str]] = mapped_column(Text)
    tags: Mapped[Optional[list[str]]] = mapped_column(ARRAY(String), default=[])
    lat: Mapped[Optional[float]] = mapped_column(Float)
    lng: Mapped[Optional[float]] = mapped_column(Float)
    is_hidden: Mapped[bool] = mapped_column(Boolean, default=False)
    source_confidence: Mapped[Optional[float]] = mapped_column(Float)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    sources: Mapped[list["Source"]] = relationship(
        "Source", back_populates="event", cascade="all, delete-orphan"
    )


class SourcePlatformEnum(str):
    INSTAGRAM = "instagram"
    WEBSITE = "website"
    FACEBOOK = "facebook"
    GOOGLE_EVENTS = "google_events"
    SHOP = "shop"
    CONVENTION_CENTER = "convention_center"
    MANUAL = "manual"


class Source(Base):
    __tablename__ = "sources"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    event_id: Mapped[int] = mapped_column(Integer, ForeignKey("events.id"), nullable=False)
    platform: Mapped[str] = mapped_column(
        Enum(
            SourcePlatformEnum.INSTAGRAM,
            SourcePlatformEnum.WEBSITE,
            SourcePlatformEnum.FACEBOOK,
            SourcePlatformEnum.GOOGLE_EVENTS,
            SourcePlatformEnum.SHOP,
            SourcePlatformEnum.CONVENTION_CENTER,
            SourcePlatformEnum.MANUAL,
            name="source_platform_enum",
        ),
        nullable=False,
    )
    source_url: Mapped[str] = mapped_column(String(500), nullable=False)
    scraped_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    raw_payload: Mapped[Optional[dict]] = mapped_column(JSONB)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    event: Mapped[Event] = relationship("Event", back_populates="sources")

