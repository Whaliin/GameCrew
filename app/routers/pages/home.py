"""
Page route for the homepage,
showing a landing page for guests
and a personalized dashboard for logged-in users.
"""

from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from sqlalchemy import desc, func
from sqlalchemy.orm import Session

from app.auth.sessions import get_user
from app.database import get_db
from app.models import Friendship, Game, PlayerGameProfile, PlayerProfile
from app.utils.assets import get_game_image_url

from ._shared import templates, create_profile_context

router = APIRouter()

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
		.limit(14)
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
	context["theme"] = context["profile"]["theme"] if context["profile"] else "dark"

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