"""Load posts from a JSON file - for testing with pasted captions.

Format: a list of objects with keys
    text       (required) the caption / post body
    url        (optional) link to the post; a placeholder is generated if missing
    posted_at  (optional) ISO date or datetime the post was published
    author     (optional) account handle
    platform   (optional) defaults to "manual"; use "instagram" for IG captions
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from dateutil import parser as dateparser

from . import Post


def load_posts(path: str | Path) -> list[Post]:
    items = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(items, list):
        raise SystemExit(f"{path}: expected a JSON list of posts")

    posts: list[Post] = []
    for i, item in enumerate(items):
        text = (item.get("text") or "").strip()
        if not text:
            print(f"  skipping item {i}: no text")
            continue
        url = item.get("url")
        if not url:
            digest = hashlib.sha1(text.encode("utf-8")).hexdigest()[:16]
            # .invalid is a reserved TLD; keeps the API's HttpUrl validation happy.
            url = f"https://manual.cardradar.invalid/{digest}"
        posted_at = item.get("posted_at")
        posts.append(
            Post(
                platform=item.get("platform", "manual"),
                url=url,
                text=text,
                posted_at=dateparser.parse(posted_at) if posted_at else None,
                author=item.get("author"),
                raw=item,
            )
        )
    return posts
