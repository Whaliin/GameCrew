# GameCrew

GameCrew GitHub page

## Current Scope

- Jinja2-rendered page routes
- Router split by domain (`pages`, `auth`, `players`, `games`, `search`)
- SQLite scaffold in project root (`gamecrew.db`)
- SQLAlchemy model and schema placeholders
- API routes that intentionally return HTTP 501 TODO responses

## Project Structure

```text
GameCrew/
|-- app/
|   |-- __init__.py
|   |-- database.py
|   |-- models.py
|   |-- schemas.py
|   `-- routers/
|       |-- __init__.py
|       |-- auth.py
|       |-- games.py
|       |-- pages.py
|       |-- players.py
|       `-- search.py
|-- static/
|   `-- css/site.css
|-- templates/
|   |-- base.html
|   |-- game.html
|   `-- index.html
|-- tests/
|   `-- test_app_stubs.py
|-- main.py
|-- requirements.txt
`-- README.md
```

### What Goes Where

- `main.py`: Entry point only. Keep this minimal and avoid feature logic here.
- `app/__init__.py`: App factory and global app wiring (router registration, middleware setup, startup wiring).
- `app/database.py`: Database engine/session setup and database-related bootstrapping.
- `app/models.py`: SQLAlchemy persistence models (tables and relationships).
- `app/schemas.py`: Pydantic request/response contracts used by routes.
- `app/routers/pages.py`: HTML page routes that render Jinja2 templates.
- `app/routers/auth.py`: Auth HTTP endpoints (register/login/logout and session-related handlers).
- `app/routers/players.py`: Player profile and player game-stats endpoints.
- `app/routers/games.py`: Game catalog and single-game endpoints.
- `app/routers/search.py`: Per-game player search endpoints only.
- `templates/`: Server-rendered HTML templates. Add new page templates here.
- `static/`: Frontend assets such as CSS/JS/images used by templates.
- `tests/`: Automated tests for routes, responses, and future business logic.

### Feature Placement Guide

When adding a new feature, follow this sequence:

1. Define or update request/response schemas in `app/schemas.py`.
2. Add or update persistence entities in `app/models.py` if database storage is needed.
3. Add endpoint handlers in the correct router under `app/routers/`.
4. If the feature is page-based, add/update templates in `templates/` and static assets in `static/`.
5. Register new router modules in `app/__init__.py` if you create a new router file.
6. Add tests in `tests/` covering happy path and expected error responses.

### Domain Routing Conventions

- API endpoints should stay under `/api/...`.
- Page routes should remain non-API routes (for example `/` and `/game/{game_slug}`).
- Search stays per-game in first implementation scope (for example `/api/search/games/{game_slug}/players`).
- Global search should not be added until requirements explicitly include it.

## Local Setup (Windows + macOS)

1. Create a virtual environment:

```bash
# Windows
python -m venv .venv

# macOS
python3 -m venv .venv
```

2. Activate the virtual environment:

```bash
# Windows (PowerShell)
.\.venv\Scripts\Activate.ps1

# macOS
source .venv/bin/activate
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Run the app:

```bash
uvicorn main:app --reload
```

5. Open in browser:

- Home page: `http://127.0.0.1:8000/`
- Example game page: `http://127.0.0.1:8000/game/counterstrike`
- API docs: `http://127.0.0.1:8000/docs`

## Run Tests

```powershell
pytest -q
```

The `tests/` folder contains starter examples for page rendering and stub API behavior.

## Stub Endpoint Examples

- `POST /api/auth/register`
- `POST /api/auth/login`
- `POST /api/auth/logout`
- `GET /api/players/{username}`
- `GET /api/players/{username}/stats/{game_slug}`
- `GET /api/games/`
- `GET /api/games/{game_slug}`
- `GET /api/search/games/{game_slug}/players?q=query`

All API endpoints above currently return HTTP 501 with a TODO detail message.

## Notes For Next Implementation Pass

- Keep per-game search as the first real search implementation.
- Keep global search out of scope until requirements include it.
- Add session-backed auth implementation under `app/routers/auth.py`.
- Add repository/service layers as persistence logic grows.
