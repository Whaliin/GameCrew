import datetime
import json
from random import random
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Game, Player, PlayerProfile, PlayerGameProfile
from app.routers.pages import get_game_image_url

router = APIRouter(prefix="/api/players", tags=["players"])

def map_age_range(birth_year: int) -> str:
	"""Map birth year to a coarse age range used in templates."""
	age = datetime.datetime.now().year - birth_year
	if age < 18:
		return "Under 18" # This case should be prevented by validation
	if age <= 25:
		return "18-25"
	if age <= 35:
		return "26-35"
	if age <= 45:
		return "36-45"
	return "45+"

def create_profile_object(db: Session, username: str) -> dict | None:
	"""Create a profile object for a given username, or return None if user not found."""
	# find the player by username
	player = db.query(Player).filter(Player.username == username).first()
	if not player:
		return None
	
	# TODO: Add the avatar stuff
	# Check if the player has an avatar (check file path based on player_id)

	

	# build the profile object
	profile = {
		"username": player.username,
		"avatar_url": "/static/img/profiles/default.jpg",
		"discord": player.profile.discord if player.profile.discord else "Not set",
		"steam": player.profile.steam_url if player.profile.steam_url else "Not set",
		"age_range": map_age_range(player.profile.birth_year),
		"region": player.profile.region.name if player.profile.region else "Unknown",
		"platforms": " / ".join([platform.name for platform in player.platforms]) if player.platforms else "Not set",
		"playtimes": " / ".join([playtime.name for playtime in player.playtimes]) if player.playtimes else "Not set",
		"languages": " / ".join([language.name for language in player.languages]) if player.languages else "Not set",
		"bio": player.profile.bio or "",
	}

	return profile

@router.get("/{username}")
def get_player_profile(username: str, db: Session = Depends(get_db)):
	profile = create_profile_object(db, username)
	if not profile:
		raise HTTPException(status_code=404, detail="Player not found")

	# Fetch player's actual game profiles
	player = db.query(Player).filter(Player.username == username).first()
	if not player:
		raise HTTPException(status_code=404, detail="Player not found")
	
	player_game_profiles = db.query(PlayerGameProfile).filter(
		PlayerGameProfile.player_id == player.id
	).all()

	profile["games"] = []
	for pgp in player_game_profiles:
		game = pgp.player  # This should be the game, but PlayerGameProfile doesn't have direct game relationship in the schema
		# Let me query the game properly
		game = db.query(Game).filter(Game.id == pgp.game_id).first()
		if game:
			game_data = {
				"slug": game.slug,
				"image_url": get_game_image_url(game.slug),
				"name": game.name,
			}
			# Add game-specific profile data if it exists
			if pgp.data:
				try:
					game_data["profile_data"] = json.loads(pgp.data)
				except json.JSONDecodeError:
					pass
			profile["games"].append(game_data)

	return profile