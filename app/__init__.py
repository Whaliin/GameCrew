"""
Application factory and setup for the API
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.database import init_database

from app.routers.pages import router as pages_router
from app.routers.pages import exception as exc_handler
from app.routers.auth import router as auth_router

from app.routers.api import router as api_router

from starlette.exceptions import HTTPException

@asynccontextmanager
async def lifespan(app: FastAPI):
	"""Lifespan event handler for startup/shutdown tasks."""
	# Startup tasks
	init_database()
	yield
	# Shutdown tasks (if any) can be added here

def create_app() -> FastAPI:
	"""Create and configure the FastAPI application."""
	app = FastAPI(title="GameCrew API", version="0.1.0", lifespan=lifespan)

	# Mount static files for CSS/JS assets
	app.mount("/static", StaticFiles(directory="static"), name="static")
	
	# Include page router
	app.include_router(pages_router)

	# Include api router
	app.include_router(api_router)

	# Include auth router
	app.include_router(auth_router)

	app.add_exception_handler(HTTPException, exc_handler.http_exception_handler)
	app.add_exception_handler(Exception, exc_handler.http_exception_handler)

	return app


def get_app_status() -> dict[str, str]:
	"""Return app diagnostics status payload."""
	return {"status": "ok", "message": "App is active."}
