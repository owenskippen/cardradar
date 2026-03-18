from __future__ import annotations

from datetime import date, time, datetime
from typing import Optional, List

from pydantic import BaseModel, HttpUrl, field_validator


class SourceBase(BaseModel):
    platform: str
    source_url: HttpUrl
    scraped_at: Optional[datetime] = None


class SourceRead(SourceBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


class EventBase(BaseModel):
    name: str
    date: Optional[date] = None
    start_time: Optional[time] = None
    end_time: Optional[time] = None
    venue: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    province: str = "BC"
    postal_code: Optional[str] = None
    organizer: Optional[str] = None
    website_url: Optional[HttpUrl] = None
    source_url_primary: Optional[HttpUrl] = None
    description: Optional[str] = None
    tags: List[str] = []
    lat: Optional[float] = None
    lng: Optional[float] = None
    is_hidden: bool = False

    @field_validator("tags", mode="before")
    @classmethod
    def default_tags(cls, v):
        return v or []


class EventCreate(EventBase):
    pass


class EventUpdate(BaseModel):
    name: Optional[str] = None
    date: Optional[date] = None
    start_time: Optional[time] = None
    end_time: Optional[time] = None
    venue: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    province: Optional[str] = None
    postal_code: Optional[str] = None
    organizer: Optional[str] = None
    website_url: Optional[HttpUrl] = None
    source_url_primary: Optional[HttpUrl] = None
    description: Optional[str] = None
    tags: Optional[List[str]] = None
    lat: Optional[float] = None
    lng: Optional[float] = None
    is_hidden: Optional[bool] = None


class EventRead(EventBase):
    id: int
    created_at: datetime
    updated_at: datetime
    sources: List[SourceRead] = []

    class Config:
        from_attributes = True


class EventMapPoint(BaseModel):
    id: int
    name: str
    date: Optional[date]
    city: Optional[str]
    lat: float
    lng: float
    tags: List[str] = []

