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

	profile = {
		"username": "Eren9s",
		"user_tag": "#Eren9s",
		"avatar_url": "/static/img/profiles/default.jpg"
	}

	# Add example game data for template testing.
	context["played_games"] = [
		{"name": "Counter-Strike 2", "slug": "cs2", "image_url": "/static/img/games/csgo.jpg", "hours_played": 123},
		{"name": "League of Legends", "slug": "lol", "image_url": "/static/img/games/lol.jpg", "hours_played": 999},
		{"name": "Valorant", "slug": "valorant", "image_url": "/static/img/games/valorant.jpg", "hours_played": 456},
	]
	context["agegroup_games"] = [
		{"name": "ARC Raiders", "slug": "arcraiders", "image_url": "/static/img/games/arcraiders.jpg", "players": 5000},
		{"name": "Mobile Legends", "slug": "mobilelegends", "image_url": "/static/img/games/mobilelegends.jpg", "players": 10000},
	]
	context["trending_games"] = [
		{"name": "Apex Legends", "slug": "apex", "image_url": "/static/img/games/apexlegends.jpg"},
		{"name": "Minecraft", "slug": "minecraft", "image_url": "/static/img/games/minecraft.jpg"},
	]

	context["profile"] = profile

	return templates.TemplateResponse(request=request, name="index.html", context=context)


@router.get("/game/{game_slug}", response_class=HTMLResponse)
def game_page(request: Request, game_slug: str):
	context = build_page_context_stub("game")
	
	context["game_slug"] = game_slug

	return templates.TemplateResponse(request=request, name="game.html", context=context)

@router.get("/profile/{user_id}", response_class=HTMLResponse)
def profile_page(request: Request, user_id: str):
	context = build_page_context_stub("profile")

	# Exempeldata för testning
	context["profile"] = {
		"username": user_id,
		"user_tag": f"#{user_id}",
		"avatar_url": "/static/img/profiles/default.jpg",
		"rank": "Global Elite",
		"age_range": "18-25",
		"platform": "PC",
		"playtime": "Kvall",
		"languages": "SV / EN",
		"bio": "Passionerad FPS-spelare. Soker seriost lag for ranked!",
	}

	context["nav_games"] = [
		{"name": "Counter-Strike 2", "slug": "cs2", "image_url": "/static/img/games/csgo.jpg"},
		{"name": "League of Legends", "slug": "lol", "image_url": "/static/img/games/lol.jpg"},
		{"name": "Valorant", "slug": "valorant", "image_url": "/static/img/games/valorant.jpg"},
		{"name": "ARC Raiders", "slug": "arcraiders", "image_url": "/static/img/games/arcraiders.jpg"},
		{"name": "Mobile Legends", "slug": "mobilelegends", "image_url": "/static/img/games/mobilelegends.jpg"},
	]

	context["profile_games"] = [
		{"name": "Counter-Strike 2", "slug": "cs2", "image_url": "/static/img/games/csgo.jpg"},
		{"name": "League of Legends", "slug": "lol", "image_url": "/static/img/games/lol.jpg"},
		{"name": "Valorant", "slug": "valorant", "image_url": "/static/img/games/valorant.jpg"},
		{"name": "Mobile Legends", "slug": "mobilelegends", "image_url": "/static/img/games/mobilelegends.jpg"},
		{"name": "ARC Raiders", "slug": "arcraiders", "image_url": "/static/img/games/arcraiders.jpg"},
		{"name": "Apex Legends", "slug": "apex", "image_url": "/static/img/games/apexlegends.jpg"},
	]

	return templates.TemplateResponse(request=request, name="profile.html", context=context)
