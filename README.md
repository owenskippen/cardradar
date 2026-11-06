# CardRadar

Find Pokémon and trading card shows near you: dates, hours, venue, admission, vendor tables and ticket links in one mobile-first web app.

Launch area: **Vancouver / Richmond / Lower Mainland**, then all of BC. Alberta, Toronto/GTA and the US are stubbed in `frontend/src/lib/regions.ts` as "coming soon".

## Structure

```
backend/   FastAPI + PostgreSQL (SQLAlchemy, Alembic)
frontend/  React + Vite + TypeScript + Tailwind (installable PWA)
```

## Run the frontend

```bash
cd frontend
npm install
npm run dev        # http://localhost:5173
```

If the backend isn't running, the app shows clearly-labelled **demo data** (`src/lib/sample.ts`) so UI work can happen on its own.
`/api` requests are proxied to `http://localhost:8000` in dev; set `VITE_API_URL` for production.

## Run the backend

Requires PostgreSQL.

```bash
cd backend
python -m venv .venv && .venv/Scripts/activate   # Windows; use bin/activate on macOS/Linux
pip install -e .
set DATABASE_URL=postgresql+psycopg://postgres:postgres@localhost:5432/cardradar
alembic upgrade head
uvicorn app.main:app --reload
```

Add shows through the admin API (`X-Api-Key: $ADMIN_API_KEY`):

```bash
curl -X POST localhost:8000/api/admin/events -H "X-Api-Key: changeme-admin-key" -H "Content-Type: application/json" \
  -d '{"name":"Example Show","date":"2026-12-05","start_time":"10:00","city":"Richmond","venue":"...","ticket_url":"https://...","table_count":60,"admission":"$5","tags":["pokemon"]}'
```

## Public API

- `GET /api/events?province=BC&country=CA&city=&start_date=&end_date=&tags=&search=`
- `GET /api/events/map`: lightweight points for the map
- `GET /api/events/{id}`
