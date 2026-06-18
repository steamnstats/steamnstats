# SteamNStats

SteamNStats is a Steam library value dashboard. It signs users in with Steam
OpenID, imports their owned games through the Steam Web API, caches store
metadata, and estimates current library value from available Steam price data.

The app does not scrape SteamDB. SteamDB has no public API and disallows
automated scraping/crawling, so historical-low price features are left as
nullable future-provider fields.

## Stack

- Backend: FastAPI, SQLModel, Alembic, PostgreSQL, Redis, APScheduler
- Frontend: TypeScript, Vite, React
- Runtime: Docker Compose for API, frontend, Postgres, Redis, and worker

## Local Setup

1. Copy the example env file:

   ```bash
   cp .env.example .env
   ```

2. Fill in `STEAM_WEB_API_KEY`, `JWT_SECRET_KEY`, and
   `JWT_REFRESH_SECRET_KEY`.

3. Start the stack:

   ```bash
   docker compose up --build
   ```

The frontend runs on `http://localhost:5173` and the API runs on
`http://localhost:8000`. The backend applies database migrations on startup.

## Mock Steam API

For local development without calling Steam, point the app at the mock service:

```bash
STEAM_ENDPOINT_URL=http://localhost:8001 docker compose --profile mock-steam up --build
```

Or put this in `.env`:

```bash
STEAM_ENDPOINT_URL=http://localhost:8001
```

Then start the stack with:

```bash
docker compose --profile mock-steam up --build
```

The login flow and backend Steam API calls use `http://localhost:8001` exactly
as configured.

## Useful Commands

```bash
make test-backend
make test-frontend
make lint-backend
make lint-frontend
```

## Local Python With pyenv and uv

This repo is pinned to Python `3.12.11` through `.python-version`.

```bash
pyenv install 3.12.11
pyenv local 3.12.11
cd backend
uv sync --extra dev
uv run python --version
uv run pytest
```

Use `uv run ...` for backend commands so the project virtualenv and lockfile are
used consistently.

## Data Notes

Steam purchase history is not exposed through a normal third-party API flow.
The v1 metric is therefore named and rendered as estimated library value. It is
computed from cached current store prices for owned games and excludes games
whose price is unavailable.
