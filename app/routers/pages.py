from typing import Any
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

router = APIRouter(tags=["pages"])
templates = Jinja2Templates(directory="templates")


def build_page_context_stub(page_name: str) -> dict[str, Any]:
	"""Build common page context values for future template expansion."""
	return {"app_name": "GameCrew", "page_name": page_name}


@router.get("/", response_class=HTMLResponse)
def home(request: Request):
	context = build_page_context_stub("home")
	return templates.TemplateResponse(request=request, name="index.html", context=context)


@router.get("/game/{game_slug}", response_class=HTMLResponse)
def game_page(request: Request, game_slug: str):
	context = build_page_context_stub("game")
	
	context["game_slug"] = game_slug

	return templates.TemplateResponse(request=request, name="game.html", context=context)
