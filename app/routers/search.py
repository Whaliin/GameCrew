from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import (
	Game,
	LanguagePreferences,
	PlatformSelections,
	Player,
	PlayerGameFavorites,
	PlayerLanguagePreferences,
	PlayerPlatformSelections,
	PlayerPlaytimePreferences,
	PlaytimePreferences,
)

router = APIRouter(prefix="/api/search", tags=["search"])

# TODO: Add response_model for search results list payload once endpoint is implemented.
@router.get("/games/{game_slug}/players")
def search_players_for_game(
	game_slug: str,
	age_lo: int | None = Query(default=None, ge=0),
	age_hi: int | None = Query(default=None, ge=0),
	playtime: str = Query(default=""),
	platform: str = Query(default=""),
	language: str = Query(default=""),
 	rank: str = Query(default=""),
	db: Session = Depends(get_db),
):
	if age_lo is not None and age_hi is not None and age_lo > age_hi:
		raise HTTPException(status_code=400, detail="age_lo cannot be greater than age_hi")

	game = db.query(Game).filter(Game.slug == game_slug).first()
	if game is None:
		raise HTTPException(status_code=404, detail="Game not found")

	query = (
		db.query(Player)
		.join(PlayerGameFavorites, PlayerGameFavorites.player_id == Player.id)
		.filter(PlayerGameFavorites.game_id == game.id)
	)

	current_year = datetime.now().year
	if age_lo is not None:
		max_birth_year = current_year - age_lo
		query = query.filter(Player.birth_year <= max_birth_year)
	if age_hi is not None:
		min_birth_year = current_year - age_hi
		query = query.filter(Player.birth_year >= min_birth_year)

	if playtime:
		playtime_pref = db.query(PlaytimePreferences).filter(PlaytimePreferences.name == playtime).first()
		if playtime_pref is None:
			raise HTTPException(status_code=400, detail="Invalid playtime filter")
		query = query.join(
			PlayerPlaytimePreferences,
			PlayerPlaytimePreferences.player_id == Player.id,
		).filter(PlayerPlaytimePreferences.playtime_preference_id == playtime_pref.id)

	if platform:
		platform_pref = db.query(PlatformSelections).filter(PlatformSelections.name == platform).first()
		if platform_pref is None:
			raise HTTPException(status_code=400, detail="Invalid platform filter")
		query = query.join(
			PlayerPlatformSelections,
			PlayerPlatformSelections.player_id == Player.id,
		).filter(PlayerPlatformSelections.platform_selection_id == platform_pref.id)

	if language:
		language_pref = db.query(LanguagePreferences).filter(LanguagePreferences.name == language).first()
		if language_pref is None:
			raise HTTPException(status_code=400, detail="Invalid language filter")
		query = query.join(
			PlayerLanguagePreferences,
			PlayerLanguagePreferences.player_id == Player.id,
		).filter(PlayerLanguagePreferences.language_preference_id == language_pref.id)

	players = query.distinct(Player.id).all()

	results = [
		{
			"username": player.username,
			"user_tag": f"#{player.username}",
			"avatar_url": player.avatar_url or "/static/img/profiles/default.jpg",
		}
		for player in players
	]

	return {"game_slug": game_slug, "results": results}
