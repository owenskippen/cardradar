"""Reddit collector via the official Reddit API (OAuth, app-only).

Requires a Reddit "script" app (https://www.reddit.com/prefs/apps) and env vars
REDDIT_CLIENT_ID and REDDIT_CLIENT_SECRET. Optional REDDIT_USER_AGENT overrides
the default User-Agent; Reddit asks for a unique, descriptive one.

Two searches per region, both limited to the last `time_filter` (default month):
  * local subreddits (r/vancouver ...)  searched for card show words
  * trading card subreddits (r/PokemonTCG ...)  searched for the region's place names
"""

from __future__ import annotations

import os
from datetime import datetime
from typing import Iterator

import httpx

from . import Post

TOKEN_URL = "https://www.reddit.com/api/v1/access_token"
API = "https://oauth.reddit.com"
DEFAULT_USER_AGENT = "python:cardradar-ingest:v0.1"

# Card subreddits where people announce or ask about shows anywhere.
CARD_SUBREDDITS = [
    "PokemonTCG",
    "pokemoncardcollectors",
    "sportscards",
    "hockeycards",
    "baseballcards",
    "magicTCG",
    "OnePieceTCG",
]

# Used in local subreddits, where most posts have nothing to do with cards.
CARD_QUERY = '"card show" OR "cardshow" OR "card expo" OR "trading card" OR "tcg" OR "pokemon cards" OR "sports cards"'


class RedditConfigError(SystemExit):
    pass


def _creds() -> tuple[str, str]:
    client_id = os.getenv("REDDIT_CLIENT_ID")
    secret = os.getenv("REDDIT_CLIENT_SECRET")
    if not client_id or not secret:
        raise RedditConfigError(
            "Reddit collection needs REDDIT_CLIENT_ID and REDDIT_CLIENT_SECRET set "
            "(create a 'script' app at https://www.reddit.com/prefs/apps). "
            "See app/ingest/sources/reddit.py."
        )
    return client_id, secret


def _client() -> httpx.Client:
    client_id, secret = _creds()
    user_agent = os.getenv("REDDIT_USER_AGENT", DEFAULT_USER_AGENT)
    resp = httpx.post(
        TOKEN_URL,
        auth=(client_id, secret),
        data={"grant_type": "client_credentials"},
        headers={"User-Agent": user_agent},
        timeout=30,
    )
    if resp.status_code != 200 or "access_token" not in resp.json():
        raise RedditConfigError(f"Reddit rejected the app credentials ({resp.status_code}): {resp.text[:200]}")
    token = resp.json()["access_token"]
    return httpx.Client(
        base_url=API,
        headers={"Authorization": f"Bearer {token}", "User-Agent": user_agent},
        timeout=30,
    )


def _search(client: httpx.Client, subreddit: str, query: str, time_filter: str, limit: int) -> list[dict] | None:
    """Matching posts, or None if the subreddit is private, banned or doesn't exist."""
    resp = client.get(
        f"/r/{subreddit}/search",
        params={"q": query, "restrict_sr": "1", "sort": "new", "t": time_filter, "limit": limit, "raw_json": "1"},
    )
    if resp.status_code in (403, 404):
        print(f"  r/{subreddit}: not accessible ({resp.status_code}) - skipping")
        return None
    if resp.status_code != 200:
        raise RuntimeError(f"Reddit search r/{subreddit} failed ({resp.status_code}): {resp.text[:200]}")
    return [child["data"] for child in resp.json().get("data", {}).get("children", [])]


def _to_post(item: dict) -> Post | None:
    if item.get("removed_by_category") or item.get("selftext") in ("[removed]", "[deleted]"):
        return None
    permalink = item.get("permalink")
    title = (item.get("title") or "").strip()
    if not permalink or not title:
        return None

    parts = [title]
    if item.get("selftext"):
        parts.append(item["selftext"].strip())
    # Link posts: the link itself is often the event page or ticket link.
    link = item.get("url_overridden_by_dest")
    if link and "reddit.com" not in link and "redd.it" not in link:
        parts.append(f"Link: {link}")

    created = item.get("created_utc")
    author = item.get("author")
    return Post(
        platform="reddit",
        url=f"https://www.reddit.com{permalink}",
        text="\n\n".join(parts),
        # Local time, not UTC: an evening post in Vancouver is already "tomorrow" in UTC,
        # which would shift relative dates like "this Saturday".
        posted_at=datetime.fromtimestamp(created) if created else None,
        author=f"u/{author}" if author and author != "[deleted]" else None,
        raw={k: item.get(k) for k in ("id", "subreddit", "title", "url", "created_utc", "link_flair_text")},
    )


def search_posts(
    local_subreddits: list[str],
    place_query: str | None,
    card_subreddits: list[str] | None = None,
    time_filter: str = "month",
    limit: int = 50,
) -> Iterator[Post]:
    searches = [(sub, CARD_QUERY) for sub in local_subreddits]
    if place_query:
        searches += [(sub, place_query) for sub in (card_subreddits if card_subreddits is not None else CARD_SUBREDDITS)]

    with _client() as client:
        for subreddit, query in searches:
            items = _search(client, subreddit, query, time_filter, limit)
            if items is None:
                continue
            print(f"  r/{subreddit}: {len(items)} matching posts")
            for item in items:
                post = _to_post(item)
                if post:
                    yield post
