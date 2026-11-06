from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Optional


@dataclass
class Post:
    """One social post / web listing that might announce a card show."""

    platform: str  # must be a SourcePlatformEnum value: instagram, website, manual, ...
    url: str
    text: str
    posted_at: Optional[datetime] = None
    author: Optional[str] = None
    raw: dict[str, Any] = field(default_factory=dict)
