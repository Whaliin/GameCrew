# ==================================
# Page rendering routes for the main site, including homepage, game pages, profile pages, etc.
# Includes logic for gathering necessary data and context for rendering templates.
# ==================================

import json

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import desc
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.auth.sessions import get_user
from app.database import get_db
from app.models import Friendship, Game, Language, Platform, Player, PlayerGameProfile, PlayerProfile, Playtime
from app.schemas import GameProfileSpec

router = APIRouter(tags=["pages"])
templates = Jinja2Templates(directory="templates")

def create_profile_context(db: Session, request: Request, user_session: Player | None = None) -> dict | None:
	"""Create a consistent context for rendering the navbar across different pages."""
	# If user_session is not provided, attempt to get it from the request. This allows us to reuse this function in contexts where we may already have the session data available, such as within the auth router after login.
	if not user_session:
		user_session = get_user(request, db)
	
	if user_session:
		# Get the users favorite games
		user_favorite_games = db.query(Game).join(PlayerGameProfile, PlayerGameProfile.game_id == Game.id).filter(PlayerGameProfile.player_id == user_session.id).all()
		
		# Append image URLs to the favorite games
		for game in user_favorite_games:
			game.image_url = get_game_image_url(game.slug)

		profile_context = {
			"username": user_session.username,
			"avatar_url": "/static/img/profiles/default.jpg",  # TODO: Replace
			"pending_requests": get_friend_requests_count(db, user_session),
			"favorite_games": user_favorite_games,
		}

		return profile_context
	return None

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

def get_friend_requests_count(db: Session, user: PlayerProfile) -> int:
	"""Return the count of pending friend requests for the current user."""
	if not user:
		return 0
	
	return db.query(Friendship).filter(
		Friendship.receiver_id == user.id,
		Friendship.accepted == False
	).count()

def get_pending_friend_requests(db: Session, user: Player) -> list[Friendship]:
	"""Return a list of pending friend requests for the current user."""
	if not user:
		return []
	
	return db.query(Friendship).filter(
		Friendship.receiver_id == user.id,
		Friendship.accepted == False
	).all()

def get_sent_requests(db: Session, user: Player) -> list[Friendship]:
	"""Return a list of friend requests sent by the current user that are still pending."""
	if not user:
		return []
	
	return db.query(Friendship).filter(
		Friendship.sender_id == user.id,
		Friendship.accepted == False
	).all()

def get_friends(db: Session, user: Player) -> list[Player]:
	"""Return a list of friends for the current user."""
	if not user:
		return []
	
	# query for players
	# join on friendships where (sender_id or receiver_id is the user) and accepted is true
	# distinct to deduplicate
	return db.query(Player).join(Friendship, ((Friendship.receiver_id == Player.id) | (Friendship.sender_id == Player.id))).filter(
		((Friendship.sender_id == user.id) | (Friendship.receiver_id == user.id)),
		Friendship.accepted == True
	).distinct().all()


@router.get("/", response_class=HTMLResponse)
def home(request: Request, db: Session = Depends(get_db)):
	"""Get the homepage. Shows landing page for guests, dashboard for users."""
	
	current_user = get_user(request, db)
	context = {}

	# Get the most popular games among all players to show on both landing and dashboard pages.
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

	context["profile"] = create_profile_context(db, request, current_user)

	# Grab the birth year of the user to find popular games among similar age groups.
	birth_year_low = current_user.profile.birth_year - 5
	birth_year_high = current_user.profile.birth_year + 5

	agegroup_games = (
		db.query(Game, func.count(PlayerGameProfile.player_id).label("player_count"))
		.join(PlayerGameProfile, PlayerGameProfile.game_id == Game.id)
		.join(PlayerProfile, PlayerProfile.player_id == PlayerGameProfile.player_id)
		.filter(PlayerProfile.birth_year.between(birth_year_low, birth_year_high))
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
		"filter_specs": {
			field_name: field_spec["validation"]
			for field_name, field_spec in game_schema.to_form_schema()["fields"].items()
		} if game_schema else {}
	}

	context["profile"] = create_profile_context(db, request)

	return templates.TemplateResponse(request=request, name="game.html", context=context)


@router.get("/profile/{username}", response_class=HTMLResponse)
def profile_page(request: Request, username: str, db: Session = Depends(get_db)):
	"""Get a user profile page."""
	context = {}
	
	current_user = get_user(request, db)
	
	# Fetch the requested player
	player = db.query(Player).filter(Player.username == username).first()
	if not player:
		raise HTTPException(status_code=404, detail="Player not found")
	
	# Check if viewing own profile
	is_own_profile = current_user and current_user.id == player.id
	
	# Build profile context
	profile = {
		"username": player.username,
		"avatar_url": "/static/img/profiles/default.jpg",  # TODO: Replace with actual avatar
		"status": "offline",  # TODO: Implement online status tracking
		"region": player.profile.region.name if player.profile.region else None,
		"birth_year": player.profile.birth_year,
		"bio": player.profile.bio or "",
		"playtime": " / ".join([pt.name for pt in player.playtimes]) if player.playtimes else None,
		"platforms": [pf.name for pf in player.platforms] if player.platforms else [],
		"languages": [lang.name for lang in player.languages] if player.languages else [],
		"discord": player.profile.discord,
		"steam": player.profile.steam_url,
	}
	
	# Fetch favorite games with ranks
	game_profiles = db.query(Game, PlayerGameProfile).join(
		PlayerGameProfile, PlayerGameProfile.game_id == Game.id
	).filter(PlayerGameProfile.player_id == player.id).all()
	
	profile["favorite_games"] = []
	for game, game_profile in game_profiles:
		# Parse rank from game profile data if it exists
		rank = None
		if game_profile.data:
			try:
				data = json.loads(game_profile.data)
				rank = data.get("rank") or data.get("premier_rank")
			except (ValueError, TypeError):
				pass
		
		profile["favorite_games"].append({
			"game_slug": game.slug,
			"game_name": game.name,
			"image_url": get_game_image_url(game.slug),
			"rank": rank,
		})
	
	context["profile"] = profile
	context["is_own_profile"] = is_own_profile
	context["current_user"] = current_user
	
	return templates.TemplateResponse(request=request, name="profile.html", context=context)


@router.get("/settings", response_class=HTMLResponse)
def settings(request: Request):
	"""Get the settings page."""
	context = {}
	return templates.TemplateResponse(request=request, name="settings.html", context=context)


@router.get("/friends", response_class=HTMLResponse)
def friends_page(request: Request, db: Session = Depends(get_db)):
	"""Get the friends page."""
	context = {}

	current_user = get_user(request, db)

	if not current_user:
		# If somehow we got here without a user, redirect to login.
		return RedirectResponse(url="/login", status_code=302)

	context["profile"] = create_profile_context(db, request, current_user)

	# Get the users friends and pending friend requests
	friends = get_friends(db, current_user)
	friendships_pending = get_pending_friend_requests(db, current_user)

	pending_requests = []
	for friendship in friendships_pending:
		# get the player profile of each sender of the pending requests (Friendship)
		sender_profile = db.query(PlayerProfile).filter(PlayerProfile.player_id == friendship.sender_id).first()
		if sender_profile:
			pending_requests.append({
				"username": sender_profile.player.username,
				"avatar_url": "/static/img/profiles/default.jpg",
				"platform": ", ".join([pf.name for pf in sender_profile.player.platforms]) if sender_profile.player.platforms else "N/A",
			})

	context["friends"] = friends
	context["pending_requests"] = pending_requests

	return templates.TemplateResponse(request=request, name="friends.html", context=context)
