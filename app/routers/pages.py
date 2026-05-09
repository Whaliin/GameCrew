from typing import Any
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import desc
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.auth.sessions import UserSession, get_user
from app.database import get_db
from app.models import Friendship, Game, Language, Platform, PlayerGameProfile, PlayerProfile, Playtime
from app.schemas import GameProfileSpec

router = APIRouter(tags=["pages"])
templates = Jinja2Templates(directory="templates")

IMG_EXTENSIONS = ("jpg", "png", "webp", "jpeg")

from pathlib import Path

STATIC_GAMES_DIR = Path("static/img/games/")

def get_game_image_url(game_slug: str) -> str:
	"""Get the image URL for a given game slug."""
	# check if the slug exists in file path
	for ext in IMG_EXTENSIONS:
		image_path = STATIC_GAMES_DIR / f"{game_slug}.{ext}"
		if image_path.exists():
			return "/" + str(image_path)
		
	# If not found, return a default image URL
	return "/static/img/games/default.jpg"

AGE_MARK_LABELS: list[str] = ["18", "25", "35", "45", "45+"]

def get_friend_requests_count(db: Session, request: Request, user: PlayerProfile) -> int:
	"""Return the count of pending friend requests for the current user."""
	if not user:
		return 0
	
	return db.query(Friendship).filter(
		Friendship.receiver_id == user.id,
		Friendship.accepted == False
	).count()

@router.get("/", response_class=HTMLResponse)
def home(request: Request, db: Session = Depends(get_db)):
	"""Get the homepage. Shows landing page for guests, dashboard for users."""
	
	current_user = get_user(request, db)
	context = {}

	most_popular_games = (
		db.query(Game, func.count(PlayerGameProfile.player_id).label("player_count"))
		.join(PlayerGameProfile, PlayerGameProfile.game_id == Game.id)
		.group_by(Game.id)
		.order_by(desc("player_count"))
		.limit(10)
		.all()
	)

	# Not logged in -> show landing/marketing page
	if current_user is None:
		# get the most popular games among all players
		context["trending_games"] = [
			{"name": game.name, "slug": game.slug, "image_url": get_game_image_url(game.slug), "player_count": pcount} 
			for game, pcount in most_popular_games
		]

		context["player_count"] = db.query(func.count(PlayerProfile.player_id)).scalar() or 0
		# TODO: Add a real squad count?
		context["squad_count"] = db.query(Friendship).filter(Friendship.accepted == True).count() or 0
		context["game_count"] = db.query(func.count(Game.id)).scalar() or 0

		return templates.TemplateResponse(request=request, name="landing.html", context=context)
	
	# Logged in -> show dashboard with personalized game and player recommendations

	favorite_games = db.query(Game).join(PlayerGameProfile, PlayerGameProfile.player_id == current_user.id).all()

	context["favorite_games"] = favorite_games

	context["profile"] = {
		"username": current_user.username,
		# TODO: Replace with actual filepath check to check if player_id has avatar set
		"avatar_url": "/static/img/profiles/default.jpg",
		"pending_requests": get_friend_requests_count(db, request, current_user),
	}

	agegroup_games = (
		db.query(Game, func.count(PlayerGameProfile.player_id).label("player_count"))
		.join(PlayerGameProfile, PlayerGameProfile.game_id == Game.id)
		.join(PlayerProfile, PlayerProfile.player_id == PlayerGameProfile.player_id)
		.filter(PlayerProfile.birth_year.between(1990, 2005))  # TODO: replace with actual user age group
		.group_by(Game.id)
		.order_by(desc("player_count"))
		.limit(10)
		.all()
	)

	context["agegroup_games"] = [
		# Get the most popular games among players roughly in the same age group as the user
		{"name": game.name, "slug": game.slug, "image_url": get_game_image_url(game.slug), "player_count": pcount}
		for game, pcount in agegroup_games
	]

	context["trending_games"] = [
		# Get the most popular games among all players
		{"name": game.name, "slug": game.slug, "image_url": get_game_image_url(game.slug), "player_count": pcount} 
		for game, pcount in most_popular_games
	]

	return templates.TemplateResponse(request=request, name="index.html", context=context)


@router.get("/game/{game_slug}", response_class=HTMLResponse)
def game_page(request: Request, game_slug: str, db: Session = Depends(get_db)):
	"""Get a game-specific page with details and player search."""
	context = {}

	# get the game info
	game = db.query(Game).filter(Game.slug == game_slug).first()
	if not game:
		raise HTTPException(status_code=404, detail="Game not found")
	
	context["game"] = {
		"name": game.name,
		"slug": game.slug,
		"image_url": get_game_image_url(game.slug)
	}

	context["age_marks"] = AGE_MARK_LABELS

	game_schema = GameProfileSpec.get_schema(game.schema_spec)

	context["filter_options"] = {
		"playtimes": [pt.name for pt in db.query(Playtime).distinct()],
		"platforms": [pf.name for pf in db.query(Platform).distinct()],
		"languages": [lang.name for lang in db.query(Language).distinct()],
		"filter_specs": game_schema.VALIDATION_RULES if game_schema else None
	}

	return templates.TemplateResponse(request=request, name="game.html", context=context)

@router.get("/profile/{username}", response_class=HTMLResponse)
def profile_page(request: Request, username: str, db: Session = Depends(get_db)):
	"""Get a user profile page."""
	context = {}
	return templates.TemplateResponse(request=request, name="profile.html", context=context)

@router.get("/settings", response_class=HTMLResponse)
def settings(request: Request):
	"""Get the settings page."""
	context = {}
	return templates.TemplateResponse(request=request, name="settings.html", context=context)

@router.get("/friends", response_class=HTMLResponse)
def friends_page(request: Request):
	"""Get the friends page."""
	context = {}
	return templates.TemplateResponse(request=request, name="friends.html", context=context)
