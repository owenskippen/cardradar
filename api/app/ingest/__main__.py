"""CLI: python -m app.ingest {file,instagram,reddit} ...

Examples (run from api/):
  python -m app.ingest file ingest_samples/captions.json --region bc
  python -m app.ingest file captions.json --dry-run
  python -m app.ingest instagram --region bc
  python -m app.ingest instagram --region bc --accounts somecardshow,someshop --no-hashtags
  python -m app.ingest reddit --region bc --dry-run
  python -m app.ingest reddit --region bc --time week --no-card-subs

New events are saved hidden. Review them with GET /api/admin/events and
publish with PATCH /api/admin/events/{id} {"is_hidden": false}.
"""

from __future__ import annotations

import argparse
import os
import sys

from dotenv import load_dotenv


def main(argv: list[str] | None = None) -> int:
    load_dotenv()  # picks up api/.env (ANTHROPIC_API_KEY, IG_*, DATABASE_URL)

    parser = argparse.ArgumentParser(prog="python -m app.ingest", description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="source", required=True)

    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("--region", default="bc", help="region id from app/ingest/regions.py (default: bc)")
    common.add_argument("--dry-run", action="store_true", help="extract and print, don't write to the database")
    common.add_argument("--no-geocode", action="store_true", help="skip OpenStreetMap geocoding")
    common.add_argument("--skip-filter", action="store_true", help="send every post to Claude, not just keyword matches")
    common.add_argument("--recheck", action="store_true", help="re-send posts Claude previously checked and skipped")

    p_file = sub.add_parser("file", parents=[common], help="ingest posts from a JSON file")
    p_file.add_argument("path")

    p_ig = sub.add_parser("instagram", parents=[common], help="collect from the Instagram Graph API")
    p_ig.add_argument("--accounts", help="comma-separated usernames (default: region's list)")
    p_ig.add_argument("--no-hashtags", action="store_true", help="only read accounts, skip hashtag search")

    p_rd = sub.add_parser("reddit", parents=[common], help="search Reddit via the official API")
    p_rd.add_argument("--subreddits", help="comma-separated local subreddits (default: region's list)")
    p_rd.add_argument("--no-card-subs", action="store_true",
                      help="skip searching card subreddits (r/PokemonTCG ...) for the region's place names")
    p_rd.add_argument("--time", default="month", choices=["day", "week", "month", "year"],
                      help="how far back to search (default: month)")

    args = parser.parse_args(argv)

    if not os.getenv("ANTHROPIC_API_KEY") and not os.getenv("ANTHROPIC_AUTH_TOKEN"):
        print("ANTHROPIC_API_KEY is not set. Put it in api/.env or your environment.", file=sys.stderr)
        return 2

    # Imported late so --help works without a database.
    import anthropic

    from ..database import SessionLocal
    from .pipeline import ingest_posts
    from .regions import get_region

    region = get_region(args.region)

    if args.source == "file":
        from .sources.file import load_posts

        posts = load_posts(args.path)
        print(f"Loaded {len(posts)} posts from {args.path}")
    elif args.source == "reddit":
        from .sources import reddit

        subreddits = args.subreddits.split(",") if args.subreddits else region.subreddits
        posts = reddit.search_posts(
            [s.strip().removeprefix("r/") for s in subreddits if s.strip()],
            None if args.no_card_subs else region.reddit_place_query,
            time_filter=args.time,
        )
        print(f"Searching Reddit for {region.label}")
    else:
        from itertools import chain

        from .sources import instagram

        accounts = args.accounts.split(",") if args.accounts else region.accounts
        streams = []
        if not args.no_hashtags:
            streams.append(instagram.hashtag_posts(region.hashtags))
        if accounts:
            streams.append(instagram.account_posts(accounts))
        posts = chain(*streams)
        print(f"Collecting Instagram posts for {region.label}")

    with SessionLocal() as db:
        try:
            stats = ingest_posts(
                db,
                posts,
                region,
                dry_run=args.dry_run,
                do_geocode=not args.no_geocode,
                skip_filter=args.skip_filter,
                recheck=args.recheck,
            )
        except anthropic.AuthenticationError:
            print("\nAnthropic API key was rejected - check ANTHROPIC_API_KEY.", file=sys.stderr)
            return 1

    print("\n" + ("[dry run] " if args.dry_run else "") + stats.summary())
    if stats.created_ids:
        print(f"Review new events: GET /api/admin/events (ids {stats.created_ids})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
