from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.database import init_database
from app.routers import auth, pages, search
from app.routers.api import favorites, players

@asynccontextmanager
async def lifespan(app: FastAPI):
	"""Lifespan event handler for startup/shutdown tasks."""
	# Startup tasks
	init_database()
	yield
	# Shutdown tasks (if any) can be added here

def create_app() -> FastAPI:
	"""Create and configure the FastAPI application."""
	application = FastAPI(title="GameCrew API", version="0.1.0", lifespan=lifespan)

	# Mount static files for CSS/JS assets
	application.mount("/static", StaticFiles(directory="static"), name="static")
	
	# Include routers for different API sections
	application.include_router(pages.router)
	application.include_router(auth.router)
	application.include_router(players.router)
	application.include_router(search.router)
	application.include_router(favorites.router)

	return application


def get_app_status() -> dict[str, str]:
	"""Return app diagnostics status payload."""
	return {"status": "ok", "message": "App is active."}
