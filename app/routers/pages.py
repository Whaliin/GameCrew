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
	current_user = build_user_content(request)
	pending_count = 2 if current_user else 0
	return {
		"nav_games": build_nav_games(request),
		"current_user": current_user,
		"pending_count": pending_count,
	}


def _get_lookup_names(db: Session, model: type) -> list[str]:
	"""Read lookup names from DB for server-rendered filter options."""
	rows = db.query(model.name).order_by(model.name.asc()).all()
	return [row.name for row in rows]


# ─────────────────────────────────────────────────────────────
# Mock profile data — replace with real DB queries when ready.
# Two sets so own-profile and other-profile look different
# while testing, but both render the full profile template.
# ─────────────────────────────────────────────────────────────
def _mock_profile_for(username: str, is_self: bool) -> dict[str, Any]:
	if is_self:
		return {
			"bio": "Long-time gamer. EU servers, mostly evenings. Down to play ranked or casual — DM me!",
			"region": "eu-west",
			"birth_year": 2000,
			"languages": ["English", "Swedish"],
			"platforms": ["PC", "PlayStation"],
			"playtime": ["Evenings", "Weekends"],
			"discord": f"{username.lower()}#0042",
			"steam": f"steamcommunity.com/id/{username.lower()}",
			"status": "online",
			"favorite_games": [
				{
					"game_slug": "cs2", "game_name": "Counter-Strike 2",
					"image_url": "/static/img/games/cs2.jpg",
					"rank": "Master Guardian II", "last_played": "Yesterday",
				},
				{
					"game_slug": "valorant", "game_name": "Valorant",
					"image_url": "/static/img/games/valorant.jpg",
					"rank": "Diamond 1", "last_played": "3 days ago",
				},
				{
					"game_slug": "lol", "game_name": "League of Legends",
					"image_url": "/static/img/games/lol.jpg",
					"rank": None, "last_played": "Last week",
				},
				{
					"game_slug": "arcraiders", "game_name": "ARC Raiders",
					"image_url": "/static/img/games/arcraiders.jpg",
					"rank": "Veteran", "last_played": "2 weeks ago",
				},
			],
			"game_ranks": [
				{
					"game_slug": "cs2", "game_name": "Counter-Strike 2",
					"game_image_url": "/static/img/games/cs2.jpg",
					"rank_name": "Master Guardian II",
				},
				{
					"game_slug": "valorant", "game_name": "Valorant",
					"game_image_url": "/static/img/games/valorant.jpg",
					"rank_name": "Diamond 1",
				},
				{
					"game_slug": "arcraiders", "game_name": "ARC Raiders",
					"game_image_url": "/static/img/games/arcraiders.jpg",
					"rank_name": "Veteran",
				},
			],
		}

	# Mock for other players — visiting somebody else's profile
	return {
		"bio": "Casual player looking for friendly squads. No toxicity, just vibes.",
		"region": "eu-north",
		"birth_year": 1998,
		"languages": ["English", "German"],
		"platforms": ["PC"],
		"playtime": ["Late night"],
		"discord": f"{username.lower()}#1337",
		"steam": None,
		"status": "online",
		"favorite_games": [
			{
				"game_slug": "valorant", "game_name": "Valorant",
				"image_url": "/static/img/games/valorant.jpg",
				"rank": "Immortal 2", "last_played": "Today",
			},
			{
				"game_slug": "lol", "game_name": "League of Legends",
				"image_url": "/static/img/games/lol.jpg",
				"rank": "Diamond IV", "last_played": "Yesterday",
			},
		],
		"game_ranks": [
			{
				"game_slug": "valorant", "game_name": "Valorant",
				"game_image_url": "/static/img/games/valorant.jpg",
				"rank_name": "Immortal 2",
			},
			{
				"game_slug": "lol", "game_name": "League of Legends",
				"game_image_url": "/static/img/games/lol.jpg",
				"rank_name": "Diamond IV",
			},
		],
	}


def _to_dict(maybe_obj: Any) -> dict[str, Any]:
	"""Coerce a profile result into a plain dict regardless of source type."""
	if isinstance(maybe_obj, dict):
		return dict(maybe_obj)
	if maybe_obj is None:
		return {}
	# SQLAlchemy / dataclass / Pydantic instances
	if hasattr(maybe_obj, "model_dump"):
		return maybe_obj.model_dump()
	if hasattr(maybe_obj, "__dict__"):
		return {k: v for k, v in vars(maybe_obj).items() if not k.startswith("_")}
	return {}


def create_profile_context(request: Request, username: str, db: Session) -> dict[str, Any]:
	"""Return context for profile page rendering."""
	context = prepare_template_context(request)

	current = context["current_user"]
	is_own_profile = bool(current and current["username"] == username)

	# Get whatever the existing route knows about this user (DB)
	db_profile = _to_dict(create_profile_object(db, username))

	# Merge DB data with mock fields the template needs
	mock = _mock_profile_for(username, is_own_profile)
	profile = {
		"username": db_profile.get("username", username),
		"user_tag": db_profile.get("user_tag", f"#{username}"),
		"avatar_url": db_profile.get("avatar_url", "/static/img/profiles/default.jpg"),
		# DB value wins, otherwise fall back to mock
		"bio": db_profile.get("bio") or mock["bio"],
		"region": db_profile.get("region") or mock["region"],
		"age": db_profile.get("age"),
		"birth_year": db_profile.get("birth_year") or mock["birth_year"],
		"languages": db_profile.get("languages") or mock["languages"],
		"platforms": db_profile.get("platforms") or mock["platforms"],
		"playtime": db_profile.get("playtime") or mock["playtime"],
		"discord": db_profile.get("discord") or mock["discord"],
		"steam": db_profile.get("steam") or mock["steam"],
		"status": db_profile.get("status") or mock["status"],
		"favorite_games": db_profile.get("favorite_games") or mock["favorite_games"],
		"game_ranks": db_profile.get("game_ranks") or mock["game_ranks"],
	}

	context["profile"] = profile
	context["is_own_profile"] = is_own_profile
	return context


@router.get("/", response_class=HTMLResponse)
def home(request: Request):
	"""Get the homepage. Shows landing page for guests, dashboard for users."""
	context = prepare_template_context(request)

	# Not logged in → show landing/marketing page
	if context["current_user"] is None:
		return templates.TemplateResponse(request=request, name="landing.html", context=context)

	# Logged in → show the actual home dashboard
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
		{"username": "Vipergg", "user_tag": "#vipergg", "avatar_url": "/static/img/profiles/default.jpg", "rank": "Diamond III", "age": 24, "discord": "vipergg#0001", "platform": "PC"},
		{"username": "NightOwl_42", "user_tag": "#nightowl", "avatar_url": "/static/img/profiles/default.jpg", "rank": "Platinum", "age": 27, "discord": "nightowl#1234", "platform": "PlayStation"},
		{"username": "kira", "user_tag": "#kira", "avatar_url": "/static/img/profiles/default.jpg", "rank": "Immortal", "age": 22, "discord": "kira", "platform": "PC"},
		{"username": "ProPlayer99", "user_tag": "#proplayer99", "avatar_url": "/static/img/profiles/default.jpg", "rank": "Global Elite", "age": 25, "discord": "pp99#0042", "platform": "PC"},
		{"username": "casual_cat", "user_tag": "#casualcat", "avatar_url": "/static/img/profiles/default.jpg", "rank": "Gold", "age": 19, "discord": None, "platform": "Switch"},
		{"username": "Stormbreaker", "user_tag": "#stormbreaker", "avatar_url": "/static/img/profiles/default.jpg", "rank": "Master", "age": 30, "discord": "storm#9999", "platform": "Xbox"},
		{"username": "ZenSniper", "user_tag": "#zensniper", "avatar_url": "/static/img/profiles/default.jpg", "rank": "Ascendant", "age": 21, "discord": "zen#0007", "platform": "PC"},
		{"username": "BobTheBuilder", "user_tag": "#bob", "avatar_url": "/static/img/profiles/default.jpg", "rank": "Veteran", "age": 35, "discord": "bob#2024", "platform": "PC"},
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
	return templates.TemplateResponse(request=request, name="profile.html", context=context)


@router.get("/settings", response_class=HTMLResponse)
def settings(request: Request):
	"""Get the settings page."""
	context = prepare_template_context(request)
	if context["current_user"] is None:
		return RedirectResponse(url="/login", status_code=303)

	# Pre-fill profile fields with current values where possible
	current = context["current_user"]
	context["profile"] = {
		"username": current["username"],
		# These come from DB once you wire them up
		"region": "eu-west",
		"birth_year": 2000,
		"languages": ["English", "Swedish"],
		"platforms": ["PC"],
		"playtime": ["Evenings", "Weekends"],
		"discord": f"{current['username'].lower()}#0042",
		"steam": "",
		"bio": "",
		"visibility": "public",
	}
	context["filter_options"] = {
		"platform": ["PC", "PlayStation", "Xbox", "Switch", "Mobile"],
		"language": [
			"English", "Swedish", "Norwegian", "Danish", "Finnish",
			"German", "French", "Spanish", "Portuguese", "Italian",
			"Dutch", "Polish", "Russian", "Ukrainian", "Turkish",
			"Arabic", "Hebrew", "Mandarin", "Cantonese", "Japanese",
			"Korean", "Vietnamese", "Thai", "Indonesian", "Hindi",
			"Greek", "Czech", "Hungarian", "Romanian",
		],
		"playtime": ["Mornings", "Afternoons", "Evenings", "Late night", "Weekends"],
	}
	return templates.TemplateResponse(request=request, name="settings.html", context=context)


@router.get("/friends", response_class=HTMLResponse)
def friends_page(request: Request):
	"""Get the friends page."""
	context = prepare_template_context(request)
	if context["current_user"] is None:
		return RedirectResponse(url="/login", status_code=303)

	# Mock data - replace with database queries when friend system exists
	context["friends"] = [
		{"username": "kira", "rank": "Diamond III", "status": "online", "avatar_url": "/static/img/profiles/default.jpg"},
		{"username": "Vipergg", "rank": "Master", "status": "online", "avatar_url": "/static/img/profiles/default.jpg"},
		{"username": "NightOwl_42", "rank": "Platinum", "status": "away", "avatar_url": "/static/img/profiles/default.jpg"},
		{"username": "casual_cat", "rank": "Gold", "status": "offline", "avatar_url": "/static/img/profiles/default.jpg"},
	]
	context["pending_requests"] = [
		{"username": "ProPlayer99", "rank": "Global Elite", "platform": "PC", "sent_at": "2 hours ago", "avatar_url": "/static/img/profiles/default.jpg"},
		{"username": "ZenSniper", "rank": "Ascendant", "platform": "PC", "sent_at": "1 day ago", "avatar_url": "/static/img/profiles/default.jpg"},
	]
	context["pending_count"] = len(context["pending_requests"])
	return templates.TemplateResponse(request=request, name="friends.html", context=context)