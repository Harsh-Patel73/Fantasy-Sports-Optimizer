# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

BetterBets is a sports betting line comparison tool that aggregates player prop data from Pinnacle and PrizePicks, normalizes stat naming, and identifies discrepancies between books.

## Commands

### Running the Application

```bash
python main.py              # Run scrapers, then start web server at http://localhost:5000
python main.py --no-scrape  # Start server only (skip scraping, use existing data)
python main.py --scrape-only # Run scrapers only (no server)
```

### Demo Mode (SQLite, no MySQL required)

```bash
# Windows
set DEMO_MODE=true
python main.py --no-scrape

# Mac/Linux
DEMO_MODE=true python main.py --no-scrape
```

### Frontend Development (hot reload)

```bash
# Terminal 1: Start backend
python main.py --no-scrape

# Terminal 2: Start Vite dev server
cd frontend
npm run dev
```

Frontend dev server runs at http://localhost:5173 and proxies `/api` to Flask.

### Frontend Build

```bash
cd frontend
npm run build    # Outputs to app/static/
npm run preview  # Preview production build
```

### Seed Demo Data

```bash
python scripts/seed_demo.py
```

## Architecture

**Flask + React Monolith**: Flask serves both the REST API and the built React frontend from `app/static/`.

### Backend Structure (app/)

- `api/routes/` - Flask blueprint routes (health, lines, discrepancies, filters)
- `api/services/` - Business logic layer (line_service, comparison_service, filter_service)
- `models/` - SQLAlchemy ORM models (books, matchups, props, statlines)
- `scrapers/` - Data extractors (pinnacle.py, prizepicks.py), orchestrated by `run_all_scrapers()`
- `db/` - Database session management and setup
- `utils/stat_mapping.py` - Canonical stat name normalization across scrapers

### Frontend Structure (frontend/src/)

- `pages/` - Route-level components (HomePage, LinesPage, DiscrepanciesPage)
- `components/` - Reusable UI (LineTable, DiscrepancyTable, FilterPanel, Layout)
- `context/FilterContext.jsx` - Global filter state via React Context + useReducer
- `api/client.js` - Fetch wrapper for API calls

### Key Patterns

- **Service Layer**: Routes delegate to services for data operations
- **Factory Pattern**: `create_app()` in `app/api/__init__.py` for Flask app creation
- **Dual-Mode Database**: `DEMO_MODE=true` uses SQLite (`demo/demo.db`), otherwise MySQL

## Configuration

Environment variables in `.env` (see `.env.example`):
- `DEMO_MODE` - `true` for SQLite demo, `false` for MySQL production
- `DB_HOST`, `DB_PORT`, `DB_USER`, `DB_PASSWORD`, `DB_NAME` - MySQL connection (production only)
- `SECRET_KEY` - Flask secret key

Config selection in `config.py`: `get_config()` returns `DemoConfig` or `ProductionConfig` based on `DEMO_MODE`.

## API Endpoints

| Endpoint | Description |
|----------|-------------|
| `GET /api/health` | Health check |
| `GET /api/lines` | Lines with filters: `book`, `team`, `player`, `stat_type`, `page`, `per_page` |
| `GET /api/discrepancies` | Line differences with filters: `min_diff`, `stat_type`, `player`, `team` |
| `GET /api/filters/teams` | Available teams |
| `GET /api/filters/players` | Available players |
| `GET /api/filters/stat-types` | Available stat types |
