from datetime import datetime
from typing import Any
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.auth.sessions import get_current_user, get_optional_user
from app.database import get_db
from app.models import LanguagePreferences, Player, PlayerLanguagePreferences, PlayerPlatformSelections, PlatformSelections, PlayerPlaytimePreferences, PlaytimePreferences
from app.routers.players import create_profile_object

router = APIRouter(tags=["pages"])
templates = Jinja2Templates(directory="templates")


POPULAR_NAV_GAMES: list[dict[str, str]] = [
	{"name": "Counter-Strike 2", "slug": "cs2"},
	{"name": "League of Legends", "slug": "lol"},
	{"name": "Valorant", "slug": "valorant"},
	{"name": "ARC Raiders", "slug": "arcraiders"},
	{"name": "Mobile Legends", "slug": "mobilelegends"},
]

GAME_IMAGE_URLS: dict[str, str] = {
	"cs2": "/static/img/games/cs2.jpg",
	"lol": "/static/img/games/lol.jpg",
	"valorant": "/static/img/games/valorant.jpg",
	"arcraiders": "/static/img/games/arcraiders.jpg",
	"mobilelegends": "/static/img/games/mobilelegends.jpg",
	"apex": "/static/img/games/apexlegends.jpg",
	"minecraft": "/static/img/games/minecraft.jpg",
}

def build_user_content(request: Request) -> dict[str, Any] | None:
	"""Return reusable user payload that can later back API/session storage."""
	current_user = get_optional_user(request)
	if not current_user:
		return None

	username = current_user.username
	return {
		"username": username,
		"user_tag": f"#{username}",
		"avatar_url": "/static/img/profiles/default.jpg",
		"favorite_game_slugs": ["cs2", "valorant", "lol", "arcraiders", "mobilelegends"],
	}


def build_nav_games(request: Request) -> list[dict[str, str]]:
	"""Return favorite/popular game cards for navbar rendering."""
	# Map slugs to display names for easy lookup
	games_by_slug = {game["slug"]: game["name"] for game in POPULAR_NAV_GAMES}
	
	# Get user content (we use this to check if they have games)
	user_content = build_user_content(request)

	# If no user or no favorites, show popular games.
	if user_content is None:
		source_games = POPULAR_NAV_GAMES
	else:
		source_games = [
			{"slug": slug, "name": games_by_slug.get(slug, slug.title())}
			for slug in user_content["favorite_game_slugs"]
		]

	return [
		{
			"name": game["name"],
			"slug": game["slug"],
			"image_url": GAME_IMAGE_URLS.get(game["slug"], "/static/img/games/cs2.jpg"),
		}
		for game in source_games
	]

def prepare_template_context(request: Request) -> dict[str, Any]:
	"""Return reusable context for template rendering."""
	return {
		"nav_games": build_nav_games(request),
		"current_user": build_user_content(request),
	}

def create_profile_context(request: Request, username: str, db: Session) -> dict[str, Any]:
	"""Return context for profile page rendering."""
	context = prepare_template_context(request)

	context["profile"] = create_profile_object(db, username)

	return context

@router.get("/", response_class=HTMLResponse)
def home(request: Request):
	"""Get the homepage."""
	context = prepare_template_context(request)

	# Add example game data for template testing.
	context["played_games"] = [
		{"name": "Counter-Strike 2", "slug": "cs2", "image_url": "/static/img/games/cs2.jpg", "hours_played": 123},
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

	return templates.TemplateResponse(request=request, name="index.html", context=context)


@router.get("/game/{game_slug}", response_class=HTMLResponse)
def game_page(request: Request, game_slug: str):
	"""Get a game-specific page with details and player search."""
	context = prepare_template_context(request)

	context["found_players"] = []

	# TODO: "found_players" should be populated by a search query, either we do it here or via
	# an api call from the frontend. For now we just add some example data for testing the template.
	context["found_players"] = [
		{"username": "gamer123", "user_tag": "#gamer123", "avatar_url": "/static/img/profiles/default.jpg", "rank": "Gold Nova III"},
		{"username": "proplayer", "user_tag": "#proplayer", "avatar_url": "/static/img/profiles/default.jpg", "rank": "Global Elite"},
	]
	
	# Add game details to context for template rendering (this can be done on the backend)
	context["game"] = {
		"game_slug": game_slug,
		"name": game_slug.title(),
		"image_url": GAME_IMAGE_URLS.get(game_slug, "/static/img/games/cs2.jpg"),
	}

	return templates.TemplateResponse(request=request, name="game.html", context=context)

@router.get("/profile/{username}", response_class=HTMLResponse)
def profile_page(request: Request, username: str, db: Session = Depends(get_db)):
	"""Get a user profile page."""
	context = create_profile_context(request, username, db)

#
#	context["nav_games"] = [
#		{"name": "Counter-Strike 2", "slug": "cs2", "image_url": "/static/img/games/cs2.jpg"},
#		{"name": "League of Legends", "slug": "lol", "image_url": "/static/img/games/lol.jpg"},
#		{"name": "Valorant", "slug": "valorant", "image_url": "/static/img/games/valorant.jpg"},
#		{"name": "ARC Raiders", "slug": "arcraiders", "image_url": "/static/img/games/arcraiders.jpg"},
#		{"name": "Mobile Legends", "slug": "mobilelegends", "image_url": "/static/img/games/mobilelegends.jpg"},
#	]
#
#	context["profile_games"] = [
#		{"name": "Counter-Strike 2", "slug": "cs2", "image_url": "/static/img/games/cs2.jpg"},
#		{"name": "League of Legends", "slug": "lol", "image_url": "/static/img/games/lol.jpg"},
#		{"name": "Valorant", "slug": "valorant", "image_url": "/static/img/games/valorant.jpg"},
#		{"name": "Mobile Legends", "slug": "mobilelegends", "image_url": "/static/img/games/mobilelegends.jpg"},
#		{"name": "ARC Raiders", "slug": "arcraiders", "image_url": "/static/img/games/arcraiders.jpg"},
#		{"name": "Apex Legends", "slug": "apex", "image_url": "/static/img/games/apexlegends.jpg"},
#	]

#	if context["is_self"]:
#		return templates.TemplateResponse(request=request, name="profile_edit.html", context=context)

	return templates.TemplateResponse(request=request, name="profile.html", context=context)
