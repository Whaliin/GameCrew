from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

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

templates = Jinja2Templates(directory="templates")
async def http_exception_handler(request, exc):
	"""Custom handler for HTTP exceptions to render a user-friendly error page."""
	return templates.TemplateResponse(
		request=request,
		name="error.html",
		context={"request": request, "status_code": exc.status_code, "message": exc.detail},
		status_code=exc.status_code,
	)

def create_app() -> FastAPI:
	"""Create and configure the FastAPI application."""
	app = FastAPI(title="GameCrew API", version="0.1.0", lifespan=lifespan)

	# Mount static files for CSS/JS assets
	app.mount("/static", StaticFiles(directory="static"), name="static")
	
	# Include routers for different API sections
	app.include_router(pages.router)
	app.include_router(auth.router)
	app.include_router(players.router)
	app.include_router(search.router)
	app.include_router(favorites.router)

	app.add_exception_handler(HTTPException, http_exception_handler)

	return app


def get_app_status() -> dict[str, str]:
	"""Return app diagnostics status payload."""
	return {"status": "ok", "message": "App is active."}
