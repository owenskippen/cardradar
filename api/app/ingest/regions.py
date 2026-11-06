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
    ),
    "toronto": Region(
        id="toronto",
        label="Toronto / GTA",
        province="ON",
        country="CA",
        hashtags=["torontocardshow", "gtacardshow", "ontariocardshow"],
        accounts=[],
    ),
    "alberta": Region(
        id="alberta",
        label="Alberta",
        province="AB",
        country="CA",
        hashtags=["calgarycardshow", "edmontoncardshow", "albertacardshow"],
        accounts=[],
    ),
}


def get_region(region_id: str) -> Region:
    try:
        return REGIONS[region_id.lower()]
    except KeyError:
        raise SystemExit(
            f"Unknown region {region_id!r}. Known: {', '.join(sorted(REGIONS))}"
        ) from None
