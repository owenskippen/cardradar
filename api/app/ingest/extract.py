"""Turn a free-text post into structured card show records using Claude."""

from __future__ import annotations

import os
from datetime import datetime
from typing import List, Optional

import anthropic
from pydantic import BaseModel, Field

from .sources import Post

MODEL = os.getenv("CARDRADAR_EXTRACT_MODEL", "claude-opus-5-5")

KNOWN_TAGS = [
    "pokemon",
    "sports",
    "one piece",
    "magic",
    "yugioh",
    "lorcana",
    "comics",
    "toys",
    "memorabilia",
]

SYSTEM_PROMPT = f"""You read social media posts and web listings and extract trading card show events from them, for a card show finder app.

A card show here means an in-person event where vendors sell or trade trading cards (sports cards, Pokemon, Magic, One Piece, etc.): card shows, card expos, collectibles shows with card vendors, TCG markets, card swap meets. Store-run tournaments, online sales, card breaks, a shop's regular opening hours, and posts that merely sell cards are not card shows.

Rules:
- Only return shows that take place on or after the date the post was published. A recap of a past show ("thanks to everyone who came out") returns no shows.
- One post can announce several shows (e.g. a season schedule); return each one.
- Resolve relative dates ("this Saturday", "Nov 22") using the post's publish date. If the year is missing, use the next occurrence on or after the publish date. If the date can't be determined, leave it null.
- Dates as YYYY-MM-DD, times as 24-hour HH:MM. Leave anything not stated in the post null - do not guess venues, addresses or times.
- province is the two-letter code (BC, AB, ON, WA, ...). Infer it from the city when the city is unambiguous.
- name: the show's own name if given, otherwise a short descriptive name like "Surrey Card Show".
- tags: only from {KNOWN_TAGS}, for the card types the post mentions. "sports" covers hockey/baseball/basketball/football cards.
- description: one or two sentences with useful details not captured elsewhere (admission price, number of tables, vendor info, door prizes). Null if nothing extra.
- confidence: 0.0-1.0, how sure you are that this post announces a real upcoming card show with the details you extracted."""


class ExtractedShow(BaseModel):
    name: str
    date: Optional[str] = Field(description="YYYY-MM-DD")
    start_time: Optional[str] = Field(description="HH:MM 24-hour")
    end_time: Optional[str] = Field(description="HH:MM 24-hour")
    venue: Optional[str]
    address: Optional[str]
    city: Optional[str]
    province: Optional[str]
    organizer: Optional[str]
    website_url: Optional[str]
    tags: List[str]
    description: Optional[str]


class Extraction(BaseModel):
    is_card_show_post: bool
    shows: List[ExtractedShow]
    confidence: float
    reason: str = Field(description="One short sentence explaining the decision")


class ExtractionError(Exception):
    pass


_client: anthropic.Anthropic | None = None


def _get_client() -> anthropic.Anthropic:
    global _client
    if _client is None:
        _client = anthropic.Anthropic(max_retries=4)
    return _client


def _user_message(post: Post, today: datetime) -> str:
    published = post.posted_at or today
    lines = [
        f"Post published: {published:%Y-%m-%d (%A)}",
        f"Platform: {post.platform}",
    ]
    if post.author:
        lines.append(f"Author: {post.author}")
    lines.append(f"URL: {post.url}")
    lines += ["", "<post>", post.text, "</post>"]
    return "\n".join(lines)


def extract_shows(post: Post, today: datetime | None = None) -> Extraction:
    """Ask Claude for the card shows announced in `post`.

    Raises ExtractionError when Claude returns no usable result (refusal,
    truncation); lets authentication errors propagate so the run stops.
    """
    today = today or datetime.now()
    response = _get_client().beta.messages.parse(
        model=MODEL,
        max_tokens=16000,
        thinking={"type": "adaptive"},
        output_config={"effort": "medium"},
        # Re-run on another model automatically if a safety classifier declines.
        betas=["server-side-fallback-2026-07-01"],
        fallbacks="default",
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": _user_message(post, today)}],
        output_format=Extraction,
    )

    if response.stop_reason == "refusal":
        category = response.stop_details.category if response.stop_details else None
        raise ExtractionError(f"model declined (category={category})")
    if response.stop_reason == "max_tokens":
        raise ExtractionError("response truncated at max_tokens")
    if response.parsed_output is None:
        raise ExtractionError(f"no structured output (stop_reason={response.stop_reason})")
    return response.parsed_output
