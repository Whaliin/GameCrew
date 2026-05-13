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
from app.database import SessionLocal, get_db
from app.models import Friendship, Game, Language, Platform, Player, PlayerGameProfile, PlayerProfile, Playtime, Region
from app.utils.assets import get_avatar_url, get_game_image_url
from app.utils.formatters import map_age_range
from app.schemas import GameProfileSpec

router = APIRouter(tags=["pages"])
templates = Jinja2Templates(directory="templates")



def create_profile_context(db: Session, request: Request, user_session: Player | None = None) -> dict | None:
	"""Create a consistent context for rendering the navbar across different pages."""
	# If user_session is not provided, attempt to get it from the request. This allows us to reuse this function in contexts where we may already have the session data available, such as within the auth router after login.
	if not user_session:
		user_session = get_user(request, db)
	
	if not user_session:
		return None
	
	# Get the users favorite games
	user_favorite_games = db.query(Game).join(PlayerGameProfile, PlayerGameProfile.game_id == Game.id).filter(PlayerGameProfile.player_id == user_session.id).all()
	
	# Append image URLs to the favorite games
	for game in user_favorite_games:
		game.image_url = get_game_image_url(game.slug)

	profile_context = {
		"username": user_session.username,
		"avatar_url": get_avatar_url(user_session.id),
		"pending_requests": get_friend_requests_count(db, user_session),
		"favorite_games": user_favorite_games,
		"platforms": [pf.name for pf in user_session.platforms] if user_session.platforms else [],
		"playtimes": [pt.name for pt in user_session.playtimes] if user_session.playtimes else [],
		"languages": [lang.name for lang in user_session.languages] if user_session.languages else [],
		"region": user_session.profile.region.name if user_session.profile.region else None,
	}

	return profile_context

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

def is_friend(db: Session, user1: Player, user2: Player) -> bool:
	"""Check if two users are friends."""
	if not user1 or not user2:
		return False
	
	return db.query(Friendship).filter(
		((Friendship.sender_id == user1.id) & (Friendship.receiver_id == user2.id)) |
		((Friendship.sender_id == user2.id) & (Friendship.receiver_id == user1.id)),
		Friendship.accepted == True
	).first() is not None

def get_friends(db: Session, user: Player) -> list[Player]:
	"""Return a list of friends for the current user."""
	if not user:
		return []
	
	# query for players
	# join on friendships where (sender_id or receiver_id is the user) and accepted is true
	# distinct to deduplicate
	# exclude the user themselves from results
	return db.query(Player).join(Friendship, ((Friendship.receiver_id == Player.id) | (Friendship.sender_id == Player.id))).filter(
		((Friendship.sender_id == user.id) | (Friendship.receiver_id == user.id)),
		Friendship.accepted == True,
		Player.id != user.id
	).distinct().all()

# ==================================
# Page Routes
# ==================================
def http_exception_handler(request: Request, exc: Exception):
	"""Custom handler for HTTP exceptions to render a user-friendly error page."""

	profile = None
	try:
		with SessionLocal() as db:
			profile = create_profile_context(db, request)
	except:
		profile = None

	context = {
		"request": request,
		"status_code": getattr(exc, "status_code", 500),
		"message": getattr(exc, "detail", "An unexpected error occurred."),
		"profile": profile
	}

	return templates.TemplateResponse(
		request=request,
		name="error.html",
		context=context,
		status_code=getattr(exc, "status_code", 500)
	)

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

	# favorite_games = db.query(Game).join(PlayerGameProfile, PlayerGameProfile.player_id == current_user.id).all()

	context["profile"] = create_profile_context(db, request, current_user)

	context["favorite_games"] = context["profile"]["favorite_games"] if context["profile"] else []

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

	all_games_rows = db.query(Game).order_by(Game.name).all()
	context["all_games"] = [
		{"name": game.name, "slug": game.slug, "image_url": get_game_image_url(game.slug)}
		for game in all_games_rows
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
	
	user = get_user(request, db)
	
	context["game"] = {
		"name": game.name,
		"slug": game.slug,
		"image_url": get_game_image_url(game.slug),
		"is_favorite": db.query(PlayerGameProfile).filter(PlayerGameProfile.game_id == game.id, PlayerGameProfile.player_id == user.id).first() is not None if user else False
	}

	context["age_marks"] = AGE_MARK_LABELS

	game_schema = GameProfileSpec.get_schema(game.schema_spec)
	# attach filter options
	context["filter_options"] = {
		"playtimes": [pt.name for pt in db.query(Playtime).distinct()],
		"platforms": [pf.name for pf in db.query(Platform).distinct()],
		"languages": [lang.name for lang in db.query(Language).distinct()],
		"filter_specs": {
			field_name: field_spec["validation"]
			for field_name, field_spec in game_schema.to_form_schema()["fields"].items()
		} if game_schema else {}
	}

	# If this game has a schema, expose rank options and current user rank for the frontend popup
	if game_schema:
		# Build a lightweight form schema and pull the display field + allowed values (if any)
		try:
			form_schema = game_schema.to_form_schema()
			display_field = form_schema.get("display_field")
			options = []
			if display_field:
				field_meta = form_schema.get("fields", {}).get(display_field, {})
				options = field_meta.get("validation", {}).get("allowedvalues") or []
			context["rank_display_field"] = display_field
			context["rank_options_json"] = json.dumps(options)
			context["rank_display_field_json"] = json.dumps(display_field) if display_field is not None else json.dumps(None)
		except Exception:
			context["rank_display_field"] = None
			context["rank_options_json"] = json.dumps([])

	# Determine current user's rank display value (if logged in and profile exists)
	user = get_user(request, db)
	user_rank = None
	game_profile_data = {}
	if user and game_schema:
		pgp = db.query(PlayerGameProfile).filter(PlayerGameProfile.game_id == game.id, PlayerGameProfile.player_id == user.id).first()
		if pgp and pgp.data:
			try:
				game_profile_data = json.loads(pgp.data)
				user_rank = game_schema.get_display_value(game_profile_data)
			except Exception:
				user_rank = None

		# Provide full form schema and current profile data for server-rendered modal (combobox-only)
		try:
			form_schema = game_schema.to_form_schema()
			context["game_form_schema"] = form_schema
			# attach parsed profile data (dict) for pre-selecting options
			context["game_profile_data"] = game_profile_data
		except Exception:
			context["game_form_schema"] = None
			context["game_profile_data"] = {}
	context["user_rank"] = user_rank
	context["user_rank_json"] = json.dumps(user_rank) if user_rank is not None else json.dumps(None)

	context["profile"] = create_profile_context(db, request)

	return templates.TemplateResponse(request=request, name="game.html", context=context)


@router.get("/profile/{username}", response_class=HTMLResponse)
def profile_page(request: Request, username: str, db: Session = Depends(get_db)):
	"""Get a user profile page."""
	context = {}
	
	current_user = get_user(request, db)

	if current_user is None:
		# If not logged in, redirect to login page.
		return RedirectResponse(url="/login", status_code=302)
	
	# Fetch the requested player
	player = db.query(Player).filter(Player.username == username).first()
	if not player:
		raise HTTPException(status_code=404, detail="Player not found")
	
	# Check if viewing own profile
	is_own_profile = current_user and current_user.id == player.id
	my_friend = is_friend(db, current_user, player) if current_user else False
	
	# Build profile context
	profile = {
		"username": player.username,
		"avatar_url": get_avatar_url(player.id),
		"region": player.profile.region.name if player.profile.region else None,
		"age": map_age_range(player.profile.birth_year) if player.profile.birth_year else None,
		# "birth_year": player.profile.birth_year,
		"bio": player.profile.bio or "",
		"playtime": " / ".join([pt.name for pt in player.playtimes]) if player.playtimes else None,
		"platforms": [pf.name for pf in player.platforms] if player.platforms else [],
		"languages": [lang.name for lang in player.languages] if player.languages else [],
		"discord": player.profile.discord,
		"steam": player.profile.steam_url,
		"is_friend": my_friend,
	}

	# add privacy settings:
	# if the profile is private and the current user is not a friend,
	# hide the external links and other profile information until they become friends.
	if player.profile.private == True and not is_own_profile and not my_friend:
		profile["discord"] = "Private"
		profile["steam"] = "Private"
		# profile["bio"] = "This profile is private. Send a friend request to view more information about this player."
		# profile["playtime"] = None
		# profile["platforms"] = []
		# profile["languages"] = []
	
	# Fetch favorite games with ranks
	game_profiles = db.query(Game, PlayerGameProfile).join(
		PlayerGameProfile, PlayerGameProfile.game_id == Game.id
	).filter(PlayerGameProfile.player_id == player.id).all()
	
	profile["favorite_games"] = []
	for game, game_profile in game_profiles:
		# Parse display value from game profile data if it exists
		display_value = None
		if game_profile.data:
			try:
				# get the game schema for this game
				game_schema = GameProfileSpec.get_schema(game.schema_spec)

				if game_schema:
					# load data (only if schema exists)
					data = json.loads(game_profile.data)
					# get the display value from the schema
					display_value = game_schema.get_display_value(data)
				
			except (ValueError, TypeError):
				pass
		
		profile["favorite_games"].append({
			"game_slug": game.slug,
			"game_name": game.name,
			"image_url": get_game_image_url(game.slug),
			"display_value": display_value,
		})
	
	context["profile"] = create_profile_context(db, request, current_user)
	context["viewing"] = profile
	context["is_own_profile"] = is_own_profile
	context["current_user"] = current_user
	
	return templates.TemplateResponse(request=request, name="profile.html", context=context)


@router.get("/settings", response_class=HTMLResponse)
def settings(request: Request, db: Session = Depends(get_db)):
	"""Get the settings page."""
	context = {}

	current_user = get_user(request, db)
	if not current_user:
		# If somehow we got here without a user, redirect to login.
		return RedirectResponse(url="/login", status_code=302)
	
	context["profile"] 		= create_profile_context(db, request, current_user)

	# attach existing profile information to the context to pre-fill the form fields
	context["current"] = {
		"region": current_user.profile.region.name if current_user.profile.region else None,
		"birth_year": current_user.profile.birth_year,
		"private": current_user.profile.private,
		"bio": current_user.profile.bio,
		"steam": current_user.profile.steam_url,
		"discord": current_user.profile.discord,
		"platforms": [pf.name for pf in current_user.platforms] if current_user.platforms else [],
		"playtime": [pt.name for pt in current_user.playtimes] if current_user.playtimes else [],
		"languages": [lang.name for lang in current_user.languages] if current_user.languages else [],
	}

	context["regions"]   = [r[0] for r in db.query(Region.name).distinct().all()]
	context["platforms"] = [r[0] for r in db.query(Platform.name).distinct().all()]
	context["playtimes"] = [r[0] for r in db.query(Playtime.name).distinct().all()]
	context["languages"] = [r[0] for r in db.query(Language.name).distinct().all()]

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

	for friend in friends:
		friend.avatar_url = get_avatar_url(friend.id)

	pending_requests = []
	for friendship in friendships_pending:
		# get the player profile of each sender of the pending requests (Friendship)
		sender_profile = db.query(PlayerProfile).filter(PlayerProfile.player_id == friendship.sender_id).first()
		if sender_profile:
			pending_requests.append({
				"username": sender_profile.player.username,
				"avatar_url": get_avatar_url(sender_profile.player_id),
				"platform": ", ".join([pf.name for pf in sender_profile.player.platforms]) if sender_profile.player.platforms else "N/A",
			})

	context["friends"] = friends
	context["pending_requests"] = pending_requests

	return templates.TemplateResponse(request=request, name="friends.html", context=context)
