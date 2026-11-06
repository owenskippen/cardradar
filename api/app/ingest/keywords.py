"""Cheap pre-filter so only plausible card show posts are sent to Claude."""

from __future__ import annotations

import re

# Any one of these is enough on its own.
STRONG_PHRASES = [
    r"card\s*show",
    r"trading\s*card\s*(show|expo|convention|fair)",
    r"sports\s*card\s*(show|expo)",
    r"tcg\s*(show|expo|convention|market)",
    r"card\s*(expo|convention|fair|market|swap\s*meet)",
    r"collectibles?\s*(show|expo|fair)",
    r"vendor\s*tables?",
    r"tables?\s*(are\s*)?(still\s*)?available",
]

# Otherwise we need a card word AND an event word.
CARD_WORDS = [
    r"cards?",
    r"tcg",
    r"pok[eé]mon",
    r"one\s*piece",
    r"mtg",
    r"magic\s*the\s*gathering",
    r"yu-?gi-?oh",
    r"lorcana",
    r"slabs?",
    r"psa",
    r"hobby\s*box(es)?",
]
EVENT_WORDS = [
    r"show",
    r"expo",
    r"convention",
    r"vendors?",
    r"tables?",
    r"admission",
    r"doors\s*open",
    r"free\s*(entry|admission)",
    r"swap\s*meet",
    r"market",
    r"come\s*(out|by|see\s*us)",
]


def _compile(words: list[str]) -> re.Pattern[str]:
    return re.compile(r"(?<![a-z])(" + "|".join(words) + r")(?![a-z])", re.IGNORECASE)


_STRONG = _compile(STRONG_PHRASES)
_CARD = _compile(CARD_WORDS)
_EVENT = _compile(EVENT_WORDS)


def looks_like_card_show(text: str | None) -> bool:
    if not text:
        return False
    # Hashtags count too: "#vancouvercardshow" -> "vancouvercardshow".
    normalized = text.replace("#", " ")
    if _STRONG.search(normalized):
        return True
    return bool(_CARD.search(normalized) and _EVENT.search(normalized))
