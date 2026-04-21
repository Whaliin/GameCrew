from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.routers import auth, games, pages, players, search


def create_app() -> FastAPI:
	"""Create and configure the FastAPI application."""
	application = FastAPI(title="GameCrew API", version="0.1.0")

	# Mount static files for CSS/JS assets
	application.mount("/static", StaticFiles(directory="static"), name="static")
	
	# Include routers for different API sections
	application.include_router(pages.router)
	application.include_router(auth.router)
	application.include_router(players.router)
	application.include_router(games.router)
	application.include_router(search.router)

	return application


def get_app_status() -> dict[str, str]:
	"""Return app diagnostics status payload."""
	return {"status": "ok", "message": "App is active."}
