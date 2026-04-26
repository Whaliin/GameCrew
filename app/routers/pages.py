from datetime import datetime
from typing import Any
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.auth.sessions import get_current_user, get_optional_user
from app.database import get_db
from app.models import Game, LanguagePreferences, PlatformSelections, PlaytimePreferences
from app.routers.players import create_profile_object

router = APIRouter(tags=["pages"])
templates = Jinja2Templates(directory="templates")


POPULAR_NAV_GAMES: list[dict[str, str]] = [
    {"name": "Counter-Strike 2", "slug": "cs2"},
    {"name": "League of Legends", "slug": "lol"},
    {"name": "Valorant", "slug": "valorant"},
    {"name": "ARC Raiders", "slug": "arcraiders"},
    {"name": "Mobile Legends", "slug": "mobilelegends"},
    {"name": "Apex Legends", "slug": "apex"},
    {"name": "Minecraft", "slug": "minecraft"},
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

AGE_MARK_LABELS: list[str] = ["18", "25", "35", "45", "45+"]

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


def _get_lookup_names(db: Session, model: type) -> list[str]:
	"""Read lookup names from DB for server-rendered filter options."""
	rows = db.query(model.name).order_by(model.name.asc()).all()
	return [row.name for row in rows]

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
def game_page(request: Request, game_slug: str, db: Session = Depends(get_db)):
	"""Get a game-specific page with details and player search."""
	context = prepare_template_context(request)

	game = db.query(Game).filter(Game.slug == game_slug).first()
	if game is None:
		raise HTTPException(status_code=404, detail="Game not found")

	playtime_options = _get_lookup_names(db, PlaytimePreferences)
	platform_options = _get_lookup_names(db, PlatformSelections)
	language_options = _get_lookup_names(db, LanguagePreferences)

	context["found_players"] = [
    {"username": "Vipergg",     "user_tag": "#vipergg",     "avatar_url": "/static/img/profiles/default.jpg", "rank": "Diamond III"},
    {"username": "NightOwl_42", "user_tag": "#nightowl",    "avatar_url": "/static/img/profiles/default.jpg", "rank": "Platinum"},
    {"username": "kira",        "user_tag": "#kira",        "avatar_url": "/static/img/profiles/default.jpg", "rank": "Immortal"},
    {"username": "ProPlayer99", "user_tag": "#proplayer99", "avatar_url": "/static/img/profiles/default.jpg", "rank": "Global Elite"},
    {"username": "casual_cat",  "user_tag": "#casualcat",   "avatar_url": "/static/img/profiles/default.jpg", "rank": "Gold"},
    {"username": "Stormbreaker","user_tag": "#stormbreaker","avatar_url": "/static/img/profiles/default.jpg", "rank": "Master"},
    {"username": "ZenSniper",   "user_tag": "#zensniper",   "avatar_url": "/static/img/profiles/default.jpg", "rank": "Ascendant"},
    {"username": "BobTheBuilder","user_tag": "#bob",        "avatar_url": "/static/img/profiles/default.jpg", "rank": "Veteran"},
]

	context["game"] = {
		"game_slug": game.slug,
		"name": game.name,
		"image_url": GAME_IMAGE_URLS.get(game.slug, "/static/img/games/cs2.jpg"),
	}

	context["age_marks"] = AGE_MARK_LABELS
	context["filter_options"] = {
		"playtime": playtime_options,
		"platform": platform_options,
		"language": language_options,
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
