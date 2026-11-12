"""Seed known recurring Lower Mainland / BC card shows.

Each entry is one dated occurrence; the database has no recurrence rules, so
add new dates here as organizers announce them and re-run:

    python -m app.seed_shows            # insert / update
    python -m app.seed_shows --dry-run  # print what would change

Re-running is safe: shows are matched with the ingest dedupe (same date and
city, similar name or venue) and updated in place instead of duplicated.

Details come from public listings (linked in `source`); listings sometimes
disagree, so check the organizer before relying on hours or prices.
"""

from __future__ import annotations

import argparse
from datetime import date, time

from .database import SessionLocal
from .ingest.dedupe import find_duplicate
from .ingest.geocode import geocode
from .models import Event, Source

# Link rule: `ticket_url` is the organizer's page for that exact date (the
# app's main "Get tickets" button). When an organizer only publishes one page
# for the whole series, that page goes in `website_url` ("Visit site") instead.

LAZY = {
    "organizer": "Lazy Trading Cards",
    "venue": "Executive Hotel Vancouver Airport (Westminster Ballroom)",
    "address": "7311 Westminster Hwy",
    "city": "Richmond",
    "postal_code": "V6X 3K3",
    "website_url": "https://lazytradingcards.com/",
}
WEST_VAN_UBC = {
    "name": "West Van Card Show @ UBC",
    "organizer": "West Van Card Show",
    "start_time": time(10, 30),
    "end_time": time(15, 30),
    "venue": "Robert H. Lee Alumni Centre, UBC",
    "address": "6133 University Blvd",
    "city": "Vancouver",
    "admission": "$10 cash / $11 card · Kids 7 & under free",
    "website_url": "https://westvancardshow.com/ubc/",
    "tags": ["pokemon", "sports", "tcg"],
    "description": "The West Van Card Show's monthly UBC edition. Tickets at the door only.",
    "source": "https://westvancardshow.com/ubc/",
}
METAMIRAJ = {
    "organizer": "Metamiraj (Guildford Card Show)",
    "city": "Surrey",
}
SOUTH_VI = {
    "name": "South V.I. Collectibles Show",
    "start_time": time(10, 0),
    "end_time": time(15, 0),
    "venue": "Ukrainian Cultural Centre",
    "address": "3277 Douglas St",
    "city": "Victoria",
    "admission": "Free",
    "website_url": "https://www.vicollectibles.com/shows",
    "tags": ["free"],
    "source": "https://www.vicollectibles.com/shows",
}

SHOWS: list[dict] = [
    {
        **LAZY,
        "name": "Collector's Fest by Lazy Trading Cards",
        "date": date(2026, 11, 22),
        "start_time": time(11, 0),
        "end_time": time(18, 30),
        "admission": "$5 early bird online / $8 at door · VIP $10 (10am entry) · Kids under 8 free",
        "ticket_url": "https://lazytradingcards.com/products/nov22-collectors_fest-hotel-executive-yvr-1",
        "description": "Richmond card show by Lazy Trading Cards. VIPs get in at 10am. The ticket page lists closing times from 5pm to 6:30pm; confirm with the organizer.",
        "source": "https://lazytradingcards.com/products/nov22-collectors_fest-hotel-executive-yvr-1",
    },
    {
        **LAZY,
        "name": "Collector's Fest by Lazy Trading Cards",
        "date": date(2026, 12, 19),
        "end_date": date(2026, 12, 20),
        "description": "Two-day Collector's Fest. Hours and tickets not announced yet.",
        "source": "https://lazytradingcards.com/products/nov22-collectors_fest-hotel-executive-yvr-1",
    },
    *[
        {**WEST_VAN_UBC, "date": d}
        for d in (
            date(2026, 11, 29),
            date(2026, 12, 19),
            date(2027, 1, 16),
            date(2027, 2, 13),
            date(2027, 3, 13),
            # the organizer also lists "APR 13", a Tuesday; left out until confirmed
            date(2027, 5, 15),
        )
    ],
    {
        **METAMIRAJ,
        "name": "Guildford Card Show (Metamiraj)",
        "date": date(2026, 12, 13),
        "start_time": time(11, 0),
        "end_time": time(17, 0),
        "venue": "Sheraton Vancouver Guildford Hotel",
        "address": "15269 104 Ave",
        "postal_code": "V3R 1N5",
        "admission": "Free",
        "website_url": "https://metamiraj.com/our-shows/",
        "tags": ["free"],
        "description": "Monthly card show at the Sheraton Guildford in Surrey.",
        "source": "https://metamiraj.com/",
    },
    {
        **METAMIRAJ,
        "name": "Mega Miraj Show",
        "date": date(2027, 2, 6),
        "end_date": date(2027, 2, 7),
        "start_time": time(11, 0),
        "end_time": time(18, 0),
        "venue": "Aria Banquet & Convention Centre",
        "address": "12350 Pattullo Pl",
        "postal_code": "V3V 8C3",
        "admission": "Free · Free parking · Optional VIP early entry from $5",
        "table_count": 200,
        "ticket_url": "https://metamiraj.com/megamiraj/",
        "tags": ["free"],
        "description": "Two-day show from the Guildford Card Show organizer with 200 vendor tables. VIP tickets include 10am early entry; special guest osare is doing signatures and sketches.",
        "source": "https://metamiraj.com/megamiraj/",
    },
    *[
        {**SOUTH_VI, "date": d}
        for d in (date(2026, 11, 14), date(2026, 11, 28), date(2026, 12, 12), date(2026, 12, 19))
    ],
]


def seed(dry_run: bool = False) -> None:
    db = SessionLocal()
    created = updated = 0
    try:
        for raw in SHOWS:
            show = dict(raw)
            source_url = show.pop("source")
            show.setdefault("province", "BC")
            show.setdefault("country", "CA")
            show.setdefault("ticket_url", None)  # clear stale links on update
            show.setdefault("website_url", None)
            show["source_url_primary"] = source_url

            existing = find_duplicate(db, show["name"], show["date"], show.get("city"), show.get("venue"))
            label = f"{show['date']}  {show['name']} ({show.get('city')})"
            if dry_run:
                print(("update  " if existing else "create  ") + label)
                continue

            moved = existing is not None and (
                existing.address != show.get("address") or existing.venue != show.get("venue")
            )
            if existing is None or existing.lat is None or moved:
                lat, lng, precision = geocode(
                    show.get("venue"), show.get("address"), show.get("city"), show["province"], show["country"]
                )
                show.update(lat=lat, lng=lng)
                label += f"  [geocoded: {precision}]"

            if existing:
                for field, value in show.items():
                    setattr(existing, field, value)
                updated += 1
                print("updated " + label)
            else:
                event = Event(**show, is_hidden=False)
                event.sources.append(Source(platform="website", source_url=source_url))
                db.add(event)
                created += 1
                print("created " + label)
            db.flush()  # so later entries dedupe against this one
        if not dry_run:
            db.commit()
            print(f"\n{created} created, {updated} updated")
    finally:
        db.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--dry-run", action="store_true")
    seed(parser.parse_args().dry_run)
