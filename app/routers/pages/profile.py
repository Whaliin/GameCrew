"""
Page route for displaying a player's profile, including your own profile
"""

import json

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session

from app.auth.sessions import get_user
from app.database import get_db
from app.models import Player, PlayerGameProfile, Game
from app.schemas import GameProfileSpec
from app.utils.assets import get_avatar_url, get_game_image_url
from app.utils.formatters import map_age_range

from app.routers.pages._shared import templates, create_profile_context, is_friend


router = APIRouter(prefix="/profile", tags=["pages"])

@router.get("/{username}", response_class=HTMLResponse)
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
	context["theme"] = context["profile"]["theme"] if context["profile"] else "dark"
	context["viewing"] = profile
	context["is_own_profile"] = is_own_profile
	context["current_user"] = current_user
	
	return templates.TemplateResponse(request=request, name="profile.html", context=context)