"""Run posts through filter -> extract -> geocode -> dedupe -> save."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime, time
from typing import Iterable, Optional

import anthropic
from dateutil import parser as dateparser
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..models import Event, IngestedPost, IngestOutcome, Source
from .dedupe import find_duplicate
from .extract import KNOWN_TAGS, ExtractedShow, ExtractionError, extract_shows
from .geocode import geocode
from .keywords import looks_like_card_show
from .regions import Region
from .sources import Post

# Events at or above this confidence are still saved hidden; the threshold
# only drops extractions Claude itself thinks are probably wrong.
MIN_CONFIDENCE = 0.4


@dataclass
class Stats:
    posts: int = 0
    already_seen: int = 0
    previously_skipped: int = 0
    filtered_out: int = 0
    not_a_show: int = 0
    errors: int = 0
    created: int = 0
    merged: int = 0
    created_ids: list[int] = field(default_factory=list)

    def summary(self) -> str:
        return (
            f"{self.posts} posts: {self.already_seen} already ingested, "
            f"{self.previously_skipped} previously checked and skipped, "
            f"{self.filtered_out} failed keyword filter, {self.not_a_show} not upcoming shows, "
            f"{self.errors} errors -> {self.created} new hidden events, "
            f"{self.merged} merged into existing events"
        )


def _parse_date(value: Optional[str]) -> Optional[date]:
    if not value:
        return None
    try:
        return date.fromisoformat(value)
    except ValueError:
        try:
            return dateparser.parse(value).date()
        except (ValueError, OverflowError):
            return None


def _parse_time(value: Optional[str]) -> Optional[time]:
    if not value:
        return None
    try:
        return time.fromisoformat(value)
    except ValueError:
        try:
            return dateparser.parse(value).time()
        except (ValueError, OverflowError):
            return None


def _clean_url(value: Optional[str]) -> Optional[str]:
    if value and value.startswith(("http://", "https://")) and len(value) <= 500:
        return value
    return None


def _clip(value: Optional[str], n: int) -> Optional[str]:
    return value[:n] if value else value


def _source_for(post: Post, show: ExtractedShow, confidence: float) -> Source:
    return Source(
        platform=post.platform,
        source_url=post.url[:500],
        scraped_at=datetime.utcnow(),
        raw_payload={
            "text": post.text,
            "author": post.author,
            "posted_at": post.posted_at.isoformat() if post.posted_at else None,
            "extracted": show.model_dump(),
            "confidence": confidence,
            "platform_payload": post.raw,
        },
    )


def _fill_missing(event: Event, show: ExtractedShow, start: Optional[time], end: Optional[time]) -> None:
    """Merge: only fill fields the existing event doesn't have yet."""
    for attr, value in (
        ("venue", _clip(show.venue, 255)),
        ("address", _clip(show.address, 255)),
        ("organizer", _clip(show.organizer, 255)),
        ("website_url", _clean_url(show.website_url)),
        ("description", show.description),
        ("start_time", start),
        ("end_time", end),
    ):
        if value and not getattr(event, attr):
            setattr(event, attr, value)
    new_tags = [t for t in show.tags if t not in (event.tags or [])]
    if new_tags:
        event.tags = list(event.tags or []) + new_tags


def _record(db: Session, post: Post, outcome: str, reason: str | None, confidence: float | None) -> None:
    """Upsert the post into ingested_posts so later runs skip it."""
    url = post.url[:500]
    row = db.scalar(select(IngestedPost).where(IngestedPost.url == url))
    if row is None:
        db.add(IngestedPost(url=url, platform=post.platform, outcome=outcome, reason=reason, confidence=confidence))
    else:
        row.outcome, row.reason, row.confidence = outcome, reason, confidence
        row.last_checked_at = datetime.utcnow()


def ingest_posts(
    db: Session,
    posts: Iterable[Post],
    region: Region,
    *,
    dry_run: bool = False,
    do_geocode: bool = True,
    skip_filter: bool = False,
    recheck: bool = False,
) -> Stats:
    """Process posts; recheck=True re-sends posts previously skipped by Claude."""
    stats = Stats()
    today = datetime.now()
    seen_this_run: set[str] = set()

    for post in posts:
        url = post.url[:500]
        if url in seen_this_run:  # same post under several hashtags
            continue
        seen_this_run.add(url)

        stats.posts += 1
        label = post.url if len(post.url) < 70 else post.url[:67] + "..."
        print(f"\n[{stats.posts}] {label}")

        if db.scalar(select(Source.id).where(Source.source_url == url).limit(1)):
            stats.already_seen += 1
            print("  already ingested - skipping")
            continue

        if not recheck:
            prior = db.scalar(select(IngestedPost).where(IngestedPost.url == url))
            if prior is not None:
                stats.previously_skipped += 1
                print(f"  checked {prior.last_checked_at:%Y-%m-%d} ({prior.outcome}) - skipping")
                continue

        if not skip_filter and not looks_like_card_show(post.text):
            stats.filtered_out += 1
            print("  no card show keywords - skipping")
            continue

        try:
            result = extract_shows(post, today=today)
        except (anthropic.AuthenticationError, anthropic.PermissionDeniedError):
            raise
        except ExtractionError as e:
            stats.errors += 1
            print(f"  extraction failed: {e}")
            continue
        except anthropic.APIStatusError as e:
            stats.errors += 1
            print(f"  Claude API error ({e.status_code}): {e.message}")
            continue
        except anthropic.APIConnectionError as e:
            stats.errors += 1
            print(f"  Claude connection error: {e}")
            continue

        print(f"  claude: show_post={result.is_card_show_post} confidence={result.confidence:.2f} - {result.reason}")
        if not result.is_card_show_post or not result.shows or result.confidence < MIN_CONFIDENCE:
            stats.not_a_show += 1
            if not dry_run:
                _record(db, post, IngestOutcome.NOT_A_SHOW, result.reason, result.confidence)
                db.commit()
            continue

        created_here = merged_here = 0
        for show in result.shows:
            show_date = _parse_date(show.date)
            if show_date and show_date < today.date():
                print(f"  - {show.name}: {show_date} is in the past - skipping")
                continue
            start, end = _parse_time(show.start_time), _parse_time(show.end_time)
            province = (show.province or region.province).upper()[:10]
            tags = [t.lower() for t in show.tags if t.lower() in KNOWN_TAGS]
            show.tags = tags

            print(
                f"  - {show.name} | {show_date or 'no date'} {show.start_time or ''}-{show.end_time or ''} "
                f"| {show.venue or '?'}, {show.city or '?'} {province} | tags={tags}"
            )

            existing = find_duplicate(db, show.name, show_date, show.city, show.venue)
            if existing:
                print(f"    duplicate of event #{existing.id} ({existing.name}) - adding as a source")
                stats.merged += 1
                merged_here += 1
                if not dry_run:
                    _fill_missing(existing, show, start, end)
                    existing.sources.append(_source_for(post, show, result.confidence))
                    db.flush()
                continue

            lat = lng = None
            if do_geocode:
                lat, lng, precision = geocode(show.venue, show.address, show.city, province, region.country)
                print(f"    geocoded ({precision}): {lat}, {lng}")

            stats.created += 1
            created_here += 1
            if dry_run:
                continue

            event = Event(
                name=show.name[:255],
                date=show_date,
                start_time=start,
                end_time=end,
                venue=_clip(show.venue, 255),
                address=_clip(show.address, 255),
                city=_clip(show.city, 100),
                province=province,
                organizer=_clip(show.organizer, 255),
                website_url=_clean_url(show.website_url),
                source_url_primary=_clean_url(post.url),
                description=show.description,
                tags=tags,
                lat=lat,
                lng=lng,
                is_hidden=True,
                source_confidence=result.confidence,
            )
            event.sources.append(_source_for(post, show, result.confidence))
            db.add(event)
            db.flush()  # session has autoflush off; make it visible to later dedupe checks
            stats.created_ids.append(event.id)
            print(f"    saved as hidden event #{event.id}")

        if created_here:
            outcome = IngestOutcome.CREATED
        elif merged_here:
            outcome = IngestOutcome.MERGED
        else:
            outcome = IngestOutcome.PAST
            stats.not_a_show += 1

        if not dry_run:
            _record(db, post, outcome, result.reason, result.confidence)
            db.commit()

    if dry_run:
        db.rollback()
    return stats
