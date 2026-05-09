import datetime
from random import random
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Game, Player, PlayerProfile

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
		"discord": {player.discord_id} if player.discord_id else "Not set",
		"steam": {player.steam_id} if player.steam_id else "Not set",
		"age_range": map_age_range(player.birth_year),
		"region": player.region.name if player.region else "Unknown",
		"platforms": " / ".join([platform.name for platform in player.profile.platforms]) if player.profile.platforms else "Not set",
		"playtimes": " / ".join([playtime.name for playtime in player.profile.playtimes]) if player.profile.playtimes else "Not set",
		"languages": " / ".join([language.name for language in player.profile.languages]) if player.profile.languages else "Not set",
		"bio": player.bio or "",
	}

	return profile

# TODO: Add response_model=schemas.PlayerProfile (or a richer profile schema) for this endpoint.
@router.get("/{username}")
def get_player_profile(username: str, db: Session = Depends(get_db)):
	profile = create_profile_object(db, username)
	if not profile:
		raise HTTPException(status_code=404, detail="Player not found")

	# Randomly add 1-4 games to the profile for testing
	profile["games"] = [
		{"slug": "cs2", "image_url": "/static/img/games/cs2.jpg", "name": "Counter-Strike 2" }
	]

	if random() < 0.75:
		profile["games"].append({"slug": "lol", "image_url": "/static/img/games/lol.jpg", "name": "League of Legends" })

	if random() < 0.5:
		profile["games"].append({"slug": "valorant", "image_url": "/static/img/games/valorant.jpg", "name": "Valorant" })

	if random() < 0.25:
		profile["games"].append({"slug": "arcraiders", "image_url": "/static/img/games/arcraiders.jpg", "name": "ARC Raiders" })

	return profile