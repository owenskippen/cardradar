"""Address -> lat/lng via OpenStreetMap Nominatim.

Nominatim's usage policy: max 1 request/second, identify the app in the
User-Agent, cache results. Fine for the low volume this pipeline produces.
"""

from __future__ import annotations

import time
from functools import lru_cache
from typing import Optional

import httpx

URL = "https://nominatim.openstreetmap.org/search"
HEADERS = {"User-Agent": "CardRadar/0.1 (card show finder; low-volume geocoding)"}
_last_call = 0.0


@lru_cache(maxsize=1024)
def _lookup(query: str, country: str) -> Optional[tuple[float, float]]:
    global _last_call
    wait = 1.1 - (time.monotonic() - _last_call)
    if wait > 0:
        time.sleep(wait)
    _last_call = time.monotonic()
    try:
        resp = httpx.get(
            URL,
            params={"q": query, "format": "json", "limit": 1, "countrycodes": country.lower()},
            headers=HEADERS,
            timeout=15,
        )
        resp.raise_for_status()
        results = resp.json()
    except (httpx.HTTPError, ValueError) as e:
        print(f"    geocode failed for {query!r}: {e}")
        return None
    if not results:
        return None
    return float(results[0]["lat"]), float(results[0]["lon"])


def geocode(
    venue: str | None,
    address: str | None,
    city: str | None,
    province: str | None,
    country: str = "CA",
) -> tuple[Optional[float], Optional[float], str]:
    """Return (lat, lng, precision) trying most to least specific queries.

    precision is "address", "venue", "city" or "none".
    """
    place = ", ".join(p for p in (city, province) if p)
    attempts = []
    if address:
        attempts.append(("address", ", ".join(p for p in (address, place) if p)))
    if venue:
        attempts.append(("venue", ", ".join(p for p in (venue, place) if p)))
    if city:
        attempts.append(("city", place))

    for precision, query in attempts:
        hit = _lookup(query, country)
        if hit:
            return hit[0], hit[1], precision
    return None, None, "none"
