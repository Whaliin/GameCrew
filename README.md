# GameCrew

GameCrew GitHub page

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
- `tests/`: Automated tests for routes, responses, and logic.

### Feature Placement Guide

When adding a new feature, follow this sequence:

1. Define or update request/response schemas in `app/schemas.py`.
2. Add or update persistence entities in `app/models.py` if database storage is needed.
3. Add endpoint handlers in the correct router under `app/routers/`.
4. If the feature is page-based, add/update templates in `templates/` and static assets in `static/`.
5. Register new router modules in `app/__init__.py` if you create a new router file.
6. Add tests in `tests/`.

### Domain Routing Conventions

- API endpoints should stay under `/api/...`.
- Page routes should remain non-API routes (for example `/` and `/game/{game_slug}`).
- Search stays per-game (for example `/api/search/games/{game_slug}/players`).

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