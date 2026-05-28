# GameCrew

A social gaming platform to help players find teammates and connect across different games.

## Project Overview

GameCrew is a **FastAPI-based web application** that lets gamers discover teammates, manage game profiles, and build friendships across multiple titles. The platform features server-side rendering with Jinja2, session-based authentication, SQLite-backed persistence, and a split router package for cleaner app organization.

## Tech Stack

- **Framework**: FastAPI + Uvicorn
- **ORM**: SQLAlchemy
- **Database**: SQLite
- **Templates**: Jinja2 (server-side rendering)
- **Authentication**: Session-based (cookies) with bcrypt password hashing
- **Validation**: Pydantic
- **Image Handling**: Pillow

## Project Structure

```
GameCrew/
├── app/
│   ├── __init__.py           # App factory and router registration
│   ├── database.py           # SQLite setup and database initialization
│   ├── models.py             # SQLAlchemy ORM models
│   ├── schemas.py            # Pydantic request/response schemas
│   ├── seed_players.py       # Development data seeding helpers
│   ├── auth/
│   │   ├── hashing.py        # bcrypt password utilities
│   │   ├── sessions.py       # Session management and auth helpers
│   │   └── validation.py     # Input validation (username, password, etc.)
│   ├── routers/
│   │   ├── auth.py           # Register, login, logout endpoints
│   │   ├── search.py         # Player search endpoints
│   │   ├── api/
│   │   │   ├── __init__.py    # Aggregated JSON API router
│   │   │   ├── games.py      # Game catalog and favorite management
│   │   │   ├── players.py    # Player profiles and game stats
│   │   │   └── profile.py    # Current user profile endpoints
│   │   └── pages/
│   │       ├── __init__.py    # Aggregated server-rendered page router
│   │       ├── _shared.py     # Shared template/context helpers
│   │       ├── exception.py   # Custom HTTP exception page handler
│   │       ├── home.py        # Homepage / landing page
│   │       ├── game.py        # Game detail page
│   │       ├── profile.py     # User profile page
│   │       ├── settings.py    # Settings page
│   │       └── friends.py     # Friends page
│   └── utils/
│       ├── assets.py         # Avatar and game image helpers
│       └── formatters.py     # Template formatting helpers
├── static/
│   ├── css/style.css         # Application styling
│   ├── img/                  # Game thumbnails, icons, profile pictures
│   └── js/app.js             # Client-side interactivity
├── templates/
│   ├── base.html             # Base template wrapper
│   ├── index.html            # Homepage
│   ├── game.html             # Game detail page
│   ├── profile.html          # User profile page
│   ├── friends.html          # Friends list
│   ├── settings.html         # User settings
│   ├── auth/                 # Login and registration pages
│   └── partials/             # Reusable template fragments (navbar, modals)
├── main.py                   # Application entry point
├── requirements.txt          # Python dependencies
└── README.md
```

## Database & Models

GameCrew uses SQLite with SQLAlchemy ORM. Key entities:

- **Player**: User account (username, password hash, created_at)
- **PlayerProfile**: Extended profile (region, birth year, platforms, languages, playtimes)
- **Game**: Game catalog entry (name, slug, custom schema fields)
- **PlayerGameProfile**: Join table linking players to their game-specific profiles
- **Friendship**: Player-to-player relationships
- **Supporting**: Language, Platform, Playtime, Region lookups

The database auto-seeds on startup with default games and configurations.

You can seed player profiles by running the following command:
```bash
python -m app.seed_players
```
This will create 1000 randomized profiles (named player0-1000) with the password "1".

Deletes are cascade-aware in the ORM for player-owned data. Deleting a `Player` removes the related profile, game profiles, friendships, and player-owned junction rows. Deleting a `Game` removes related `PlayerGameProfile` rows.

## Authentication

GameCrew uses **session-based authentication** backed by cookies:

- **Registration**: Username, password, birth year, region validation
- **Login/Logout**: Secure session handling via middleware
- **Password Hashing**: bcrypt for secure password storage
- **Session Helpers**: Shared helpers resolve the current user from the cookie session

Register and login pages are served at `/register` and `/login`.

## Development

**Run the development server:**

```bash
uvicorn main:app --reload
```

**View API documentation:**

Open [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs) in your browser.

## Static Assets & Templates

- **CSS**: Edit `static/css/style.css` for styling changes.
- **Images**: Place game thumbnails, icons, and profile pictures in `static/img/`.
- **JavaScript**: Client-side logic in `static/js/app.js`.
- **Page Templates**: Add new pages in `templates/` and corresponding routes in `app/routers/pages/`.
- **Reusable Partials**: Shared components like the navbar are in `templates/partials/`.

## Local Setup (Windows + macOS)

1. Create a virtual environment [(What is a virtual environment?)](https://docs.python.org/3/library/venv.html):

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
python3 -m venv .venv
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
- Example game page: `http://127.0.0.1:8000/game/cs2`
- API docs: `http://127.0.0.1:8000/docs`

---

## Contributing

### Feature Checklist

When adding a new feature, follow this sequence:

1. **Schemas**: Define or update request/response schemas in `app/schemas.py`.
2. **Models**: Add or update persistence entities in `app/models.py` if database storage is needed.
3. **Handlers**: Add endpoint handlers in the correct router under `app/routers/` or `app/routers/api/`.
4. **Templates**: For page-based features, add/update templates in `templates/` and static assets in `static/`.
5. **Registration**: Register new router packages in `app/__init__.py` if you create a new router package.

### Routing Conventions

- **API endpoints**: Keep under `/api/...` (e.g., `/api/games/favorite`, `/api/players/search`).
- **Page routes**: Keep as non-API routes (e.g., `/`, `/game/{game_slug}`, `/profile/{username}`).
- **Package layout**: Group related page handlers under `app/routers/pages/` and export them through the package `__init__.py`.
- **Search**: Namespace search endpoints per-game (e.g., `/api/search/games/{game_slug}/players`).

