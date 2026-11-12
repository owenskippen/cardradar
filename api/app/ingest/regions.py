"""Regions the ingester knows about.

Instagram's hashtag search allows only 30 unique hashtags per rolling 7 days
per account, so keep each region's hashtag list short and high-signal.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class Region:
    id: str
    label: str
    province: str
    country: str
    hashtags: list[str] = field(default_factory=list)
    # Organizer / shop accounts to read via Business Discovery.
    accounts: list[str] = field(default_factory=list)
    # Reddit: local subreddits are searched for card show words; place names are
    # searched for in the card subreddits (see app/ingest/sources/reddit.py).
    subreddits: list[str] = field(default_factory=list)
    reddit_places: list[str] = field(default_factory=list)

    @property
    def reddit_place_query(self) -> str | None:
        return " OR ".join(f'"{p}"' if " " in p else p for p in self.reddit_places) or None


REGIONS: dict[str, Region] = {
    "bc": Region(
        id="bc",
        label="British Columbia",
        province="BC",
        country="CA",
        hashtags=[
            "vancouvercardshow",
            "bccardshow",
            "vancouvercards",
            "surreycardshow",
            "victoriacardshow",
            "kelownacardshow",
        ],
        accounts=[],
        subreddits=["vancouver", "britishcolumbia", "surrey", "burnaby", "VictoriaBC", "kelowna"],
        reddit_places=["vancouver", "richmond bc", "surrey bc", "burnaby", "victoria bc", "kelowna", "lower mainland"],
    ),
    "toronto": Region(
        id="toronto",
        label="Toronto / GTA",
        province="ON",
        country="CA",
        hashtags=["torontocardshow", "gtacardshow", "ontariocardshow"],
        accounts=[],
        subreddits=["toronto", "ontario", "mississauga", "brampton"],
        reddit_places=["toronto", "gta", "mississauga", "brampton", "markham"],
    ),
    "alberta": Region(
        id="alberta",
        label="Alberta",
        province="AB",
        country="CA",
        hashtags=["calgarycardshow", "edmontoncardshow", "albertacardshow"],
        accounts=[],
        subreddits=["alberta", "Calgary", "Edmonton"],
        reddit_places=["calgary", "edmonton", "alberta"],
    ),
}


def get_region(region_id: str) -> Region:
    try:
        return REGIONS[region_id.lower()]
    except KeyError:
        raise SystemExit(
            f"Unknown region {region_id!r}. Known: {', '.join(sorted(REGIONS))}"
        ) from None
