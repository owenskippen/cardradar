"""Instagram collector via the official Instagram Graph API.

UNTESTED against the live API - written to Meta's documented endpoints but not
yet run with a real token. Requires:
  * an Instagram Business or Creator account linked to a Facebook Page
  * a Meta app with the Instagram Graph API and (for hashtags) the
    "Instagram Public Content Access" feature approved
  * env vars IG_USER_ID (your IG business account id) and IG_ACCESS_TOKEN

Two collection modes:
  * hashtag search  - recent public posts for each region hashtag
                      (limit: 30 unique hashtags per rolling 7 days)
  * business discovery - recent posts from named business/creator accounts
"""

from __future__ import annotations

import os
from datetime import datetime
from typing import Iterator

import httpx
from dateutil import parser as dateparser

from . import Post

GRAPH_VERSION = os.getenv("IG_GRAPH_VERSION", "v21.0")
BASE = f"https://graph.facebook.com/{GRAPH_VERSION}"
MEDIA_FIELDS = "id,caption,permalink,timestamp,media_type"


class InstagramConfigError(SystemExit):
    pass


def _creds() -> tuple[str, str]:
    user_id = os.getenv("IG_USER_ID")
    token = os.getenv("IG_ACCESS_TOKEN")
    if not user_id or not token:
        raise InstagramConfigError(
            "Instagram collection needs IG_USER_ID and IG_ACCESS_TOKEN set "
            "(Instagram Business account + Meta app). See app/ingest/sources/instagram.py."
        )
    return user_id, token


def _get(client: httpx.Client, path: str, params: dict) -> dict:
    resp = client.get(f"{BASE}/{path}", params=params, timeout=30)
    if resp.status_code != 200:
        try:
            err = resp.json().get("error", {})
        except ValueError:
            err = {}
        raise RuntimeError(
            f"Graph API {path} failed ({resp.status_code}): {err.get('message', resp.text[:200])}"
        )
    return resp.json()


def _to_post(media: dict, author: str | None = None) -> Post | None:
    caption = media.get("caption")
    if not caption or not media.get("permalink"):
        return None
    ts = media.get("timestamp")
    posted_at: datetime | None = dateparser.parse(ts) if ts else None
    return Post(
        platform="instagram",
        url=media["permalink"],
        text=caption,
        posted_at=posted_at,
        author=author or media.get("username"),
        raw=media,
    )


def hashtag_posts(hashtags: list[str], limit_per_tag: int = 50) -> Iterator[Post]:
    user_id, token = _creds()
    with httpx.Client() as client:
        for tag in hashtags:
            tag = tag.lstrip("#").lower()
            found = _get(client, "ig_hashtag_search", {"user_id": user_id, "q": tag, "access_token": token})
            if not found.get("data"):
                print(f"  #{tag}: no hashtag id returned")
                continue
            tag_id = found["data"][0]["id"]
            media = _get(
                client,
                f"{tag_id}/recent_media",
                {"user_id": user_id, "fields": MEDIA_FIELDS, "limit": limit_per_tag, "access_token": token},
            )
            items = media.get("data", [])
            print(f"  #{tag}: {len(items)} recent posts")
            for m in items:
                post = _to_post(m)
                if post:
                    yield post


def account_posts(usernames: list[str], limit_per_account: int = 25) -> Iterator[Post]:
    user_id, token = _creds()
    with httpx.Client() as client:
        for username in usernames:
            username = username.lstrip("@")
            fields = f"business_discovery.username({username}){{media.limit({limit_per_account}){{{MEDIA_FIELDS}}}}}"
            data = _get(client, user_id, {"fields": fields, "access_token": token})
            items = data.get("business_discovery", {}).get("media", {}).get("data", [])
            print(f"  @{username}: {len(items)} recent posts")
            for m in items:
                post = _to_post(m, author=username)
                if post:
                    yield post
