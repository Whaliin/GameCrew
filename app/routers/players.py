import datetime
from random import random
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Game, Player, PlayerGameFavorites, PlaytimePreferences, PlayerPlaytimePreferences, PlatformSelections, PlayerPlatformSelections, LanguagePreferences, PlayerLanguagePreferences

router = APIRouter(prefix="/api/players", tags=["players"])

def get_preference_names(
	db: Session,
	user_id: int,
	model,
	association_model,
	association_fk_field: str,
) -> list[str]:
	"""Fetch preference names for a user given the model and association model."""
	association_fk = getattr(association_model, association_fk_field)
	rows = (
		db.query(model.name)
		.join(
			association_model,
			association_fk == model.id
		)
		.filter(association_model.player_id == user_id)
		.all()
	)
	return [row.name for row in rows]

def get_playtime_preference_names(db: Session, user_id: int) -> list[str]:
	"""Fetch playtime preference names for a user."""
	return get_preference_names(
		db,
		user_id,
		PlaytimePreferences,
		PlayerPlaytimePreferences,
		"playtime_preference_id",
	)

def get_platform_selection_names(db: Session, user_id: int) -> list[str]:
	"""Fetch platform selection names for a user."""
	return get_preference_names(
		db,
		user_id,
		PlatformSelections,
		PlayerPlatformSelections,
		"platform_selection_id",
	)

def get_language_preference_names(db: Session, user_id: int) -> list[str]:
	"""Fetch language preference names for a user."""
	return get_preference_names(
		db,
		user_id,
		LanguagePreferences,
		PlayerLanguagePreferences,
		"language_preference_id",
	)


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

	# fetch related preference names
	platform_names = get_platform_selection_names(db, player.id)
	playtimes_names = get_playtime_preference_names(db, player.id)
	language_names = get_language_preference_names(db, player.id)

	# build the profile object
	profile = {
		"username": player.username,
		"user_tag": f"#{player.username}",
		"avatar_url": player.avatar_url or "/static/img/profiles/default.jpg",
		"discord": {player.discord_id} if player.discord_id else "Not set",
		"steam": {player.steam_id} if player.steam_id else "Not set",
		"age_range": map_age_range(player.birth_year),
		"region": player.region.name if player.region else "Unknown",
		"platforms": " / ".join(platform_names) if platform_names else "Not set",
		"playtimes": " / ".join(playtimes_names) if playtimes_names else "Not set",
		"languages": " / ".join(language_names) if language_names else "Not set",
		"bio": player.bio or "",
	}

	return profile

def get_player_games(db: Session, player_id: int) -> list[dict[str, str]]:
	"""Fetch a player's favorite games."""
	rows = (
		db.query(Game.slug, Game.name)
		.join(PlayerGameFavorites, PlayerGameFavorites.game_id == Game.id)
		.filter(PlayerGameFavorites.player_id == player_id)
		.all()
	)
	return [{"slug": row.slug, "name": row.name} for row in rows]

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

# TODO: Add response_model for game-specific stats payload once implemented.
@router.get("/{username}/stats/{game_slug}")
def get_player_game_stats(username: str, game_slug: str):
	raise HTTPException(
		status_code=501,
		detail=f"TODO: fetch game stats for '{username}' in '{game_slug}'",
	)
