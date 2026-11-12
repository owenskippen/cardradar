# CardRadar

Find Pokémon and trading card shows near you: dates, hours, venue, admission, vendor tables and ticket links in one mobile-first web app.

Launch area: **Vancouver / Richmond / Lower Mainland**, then all of BC. Alberta, Toronto/GTA and the US are stubbed in `web/src/lib/regions.ts` as "coming soon".

## Structure

```
api/       FastAPI + PostgreSQL (SQLAlchemy, Alembic)
web/       React + Vite + TypeScript + Tailwind (installable PWA)
```

## Run the web app

```bash
cd web
npm install
npm run dev        # http://localhost:5173
```

If the API isn't running, the app shows clearly-labelled **demo data** (`src/lib/sample.ts`) so UI work can happen on its own.
`/api` requests are proxied to `http://localhost:8000` in dev; set `VITE_API_URL` for production.

## Run the API

Requires PostgreSQL.

```bash
cd api
python -m venv .venv && .venv/Scripts/activate   # Windows; use bin/activate on macOS/Linux
pip install -e .
set DATABASE_URL=postgresql+psycopg://postgres:postgres@localhost:5432/cardradar
python -m alembic upgrade head   # plain `alembic` can't import `app`
uvicorn app.main:app --reload
```

Load the known recurring shows (Collector's Fest, West Van, Guildford, ...) with `python -m app.seed_shows`. Add new dates to `app/seed_shows.py` as organizers announce them and re-run it; it updates existing rows rather than duplicating them.

Or add shows through the admin API (`X-Api-Key: $ADMIN_API_KEY`):

```bash
curl -X POST localhost:8000/api/admin/events -H "X-Api-Key: changeme-admin-key" -H "Content-Type: application/json" \
  -d '{"name":"Example Show","date":"2026-12-05","start_time":"10:00","city":"Richmond","venue":"...","ticket_url":"https://...","table_count":60,"admission":"$5","tags":["pokemon"]}'
```

## Ingest card shows

The ingest pipeline finds card shows in social posts: keyword filter, then Claude extraction, then geocoding, then dedupe. New shows are saved **hidden** for review. Set `ANTHROPIC_API_KEY` in `api/.env` (see `api/.env.example`).

```bash
cd api
python -m app.ingest file ingest_samples/captions.json --dry-run   # preview, writes nothing
python -m app.ingest file ingest_samples/captions.json             # save as hidden events
python -m app.ingest instagram --region bc                          # Instagram Graph API (needs IG_USER_ID / IG_ACCESS_TOKEN)
python -m app.ingest reddit --region bc --dry-run                   # Reddit API (needs REDDIT_CLIENT_ID / REDDIT_CLIENT_SECRET)
```

The Reddit source searches each region's local subreddits (`subreddits` in `app/ingest/regions.py`) for card show words, and searches the card subreddits (r/PokemonTCG, r/sportscards, ...) for the region's place names (`reddit_places`). Create a "script" app at https://www.reddit.com/prefs/apps to get the client id and secret. Use `--time week` for frequent runs and `--no-card-subs` to search only the local subreddits.

Posts Claude has already checked are recorded in `ingested_posts` and skipped on later runs; pass `--recheck` to process them again.

Publish a reviewed show with `PATCH /api/admin/events/{id}` and `{"is_hidden": false}`.

## Public API

- `GET /api/events?province=BC&country=CA&city=&start_date=&end_date=&tags=&search=`
- `GET /api/events/map`: lightweight points for the map
- `GET /api/events/{id}`
