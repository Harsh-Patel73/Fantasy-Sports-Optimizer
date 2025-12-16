# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

BetterBets is a sports betting line comparison tool that aggregates odds data from 50+ sportsbooks via The Odds API for NFL, NBA, MLB, and NHL. It normalizes stat naming and identifies discrepancies between books.

## Commands

### Running the Application

```bash
python main.py              # Fetch data from APIs, then start web server at http://localhost:5000
python main.py --no-fetch   # Start server only (skip data fetch, use existing data)
python main.py --fetch-only # Fetch data only (no server)
```

### Quick Start (SQLite database included)

```bash
python main.py --no-fetch   # Uses existing demo data in demo/demo.db
```

### Frontend Development (hot reload)

```bash
# Terminal 1: Start backend
python main.py --no-fetch

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

- `api/routes/` - Flask blueprint routes (health, lines, discrepancies, filters, comparison, parlay)
- `api/services/` - Business logic layer (line_service, comparison_service, filter_service, parlay_service)
- `models/` - SQLAlchemy ORM models (books, matchups, props, statlines)
- `data_sources/` - API integrations (theoddsapi.py), orchestrated by `sync_all_data()`
- `db/` - Database session management and setup
- `utils/stat_mapping.py` - Canonical stat name normalization across data sources

### Frontend Structure (frontend/src/)

- `pages/` - Route-level components (HomePage, DiscrepanciesPage, LineComparisonPage, ParlayBuilderPage, CalculatorsPage)
- `components/` - Reusable UI (ComparisonTable, DiscrepancyTable, FilterPanel, EVLinesList, Layout)
- `context/FilterContext.jsx` - Global filter state via React Context + useReducer
- `context/ThemeContext.jsx` - Dark/light mode theme management
- `api/client.js` - Fetch wrapper for API calls

### Key Patterns

- **Service Layer**: Routes delegate to services for data operations
- **Factory Pattern**: `create_app()` in `app/api/__init__.py` for Flask app creation
- **Dual-Mode Database**: `DEMO_MODE=true` uses SQLite (`demo/demo.db`), otherwise MySQL

## Configuration

Environment variables in `.env`:
- `DEMO_MODE` - `true` (default) uses SQLite at `demo/demo.db`
- `SECRET_KEY` - Flask secret key
- `ODDS_API_KEY` - API key for The Odds API (for fetching fresh data)

## API Endpoints

| Endpoint | Description |
|----------|-------------|
| `GET /api/health` | Health check |
| `GET /api/lines` | Lines with filters: `book`, `team`, `player`, `stat_type`, `page`, `per_page` |
| `GET /api/discrepancies` | Line differences with filters: `min_diff`, `stat_type`, `player`, `team` |
| `GET /api/compare` | Compare lines across books for the same player/stat |
| `GET /api/parlay/ev-lines` | Get +EV lines for parlay building |
| `GET /api/filters/teams` | Available teams |
| `GET /api/filters/players` | Available players |
| `GET /api/filters/stat-types` | Available stat types |
| `GET /api/filters/books` | Available sportsbooks |

## Data Source

**The Odds API** - Provides real-time odds from 50+ sportsbooks:
- Sports: NFL, NBA, MLB, NHL
- Markets: Moneyline (h2h), Spreads, Totals, Player Props
- Quota: 500 requests/month on free tier
