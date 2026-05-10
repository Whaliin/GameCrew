# ===========================
# API endpoints related to games and user game profiles.

from fastapi import APIRouter, Depends, HTTPException, Request, Response
import json
from pydantic import ValidationError
from sqlalchemy.orm import Session

from app.auth.sessions import get_user
from app.database import get_db
from app.models import Game, PlayerGameProfile
from app.schemas import GameProfileSpec

router = APIRouter(prefix="/api/games", tags=["favorites"])

def _get_game_or_404(db: Session, slug: str) -> Game:
	game = db.query(Game).filter(Game.slug == slug).first()
	if game is None:
		raise HTTPException(status_code=404, detail="Game not found")
	return game

def _get_player_game_profile(db: Session, player_id: int, game_id: int) -> PlayerGameProfile | None:
	return (
		db.query(PlayerGameProfile)
		.filter(
			PlayerGameProfile.player_id == player_id,
			PlayerGameProfile.game_id == game_id,
		)
		.first()
	)

@router.put("/{slug}/favorite")
def add_favorite(
	slug: str,
	request: Request,
	db: Session = Depends(get_db),
):
	"""Add a game to the current user's favorites."""
	user = get_user(request, db)
	if user is None:
		raise HTTPException(status_code=401, detail="Not authenticated")
	
	# Get the game
	game = _get_game_or_404(db, slug)
	
	# Check if already favorited
	existing = _get_player_game_profile(db, user.id, game.id)
	if existing is not None:
		raise HTTPException(status_code=400, detail="Game already favorited")

	# Add the favorite
	db.add(PlayerGameProfile(player_id=user.id, game_id=game.id))
	db.commit()

@router.delete("/{slug}/favorite")
def remove_favorite(
	slug: str,
	request: Request,
	db: Session = Depends(get_db),
):
	"""Remove a game from the current user's favorites."""
	user = get_user(request, db)
	if user is None:
		raise HTTPException(status_code=401, detail="Not authenticated")
	
	# Get the game
	game = _get_game_or_404(db, slug)
	
	# Check if favorited
	existing = _get_player_game_profile(db, user.id, game.id)
	if existing is None:
		raise HTTPException(status_code=400, detail="Game not in favorites")

	# Remove the favorite
	db.delete(existing)
	db.commit()

@router.post("/{slug}/info")
def set_game_profile_info(
	slug: str,
	profile_data: dict,
	request: Request,
	db: Session = Depends(get_db),
):
	"""Set or update the current user's profile data for a specific game."""
	user = get_user(request, db)
	if user is None:
		raise HTTPException(status_code=401, detail="Not authenticated")
	
	# Get the game
	game = _get_game_or_404(db, slug)
	
	# Check if favorited
	existing = _get_player_game_profile(db, user.id, game.id)
	if existing is None:
		raise HTTPException(status_code=400, detail="Game not in favorites")
	
	# Get the schema for this game, if it exists, and validate the provided profile data against it.
	game_schema = GameProfileSpec.get_schema(game.schema_spec)
	if not game_schema:
		raise HTTPException(status_code=400, detail="Profile updates not supported for this game")

	# Validate and coerce using the Pydantic schema
	try:
		schema_obj = game_schema(**profile_data)
	except ValidationError as e:
		raise HTTPException(status_code=422, detail=e.errors())

	# Canonicalize and store as JSON
	to_store = schema_obj.model_dump() if hasattr(schema_obj, "model_dump") else schema_obj.dict()
	try:
		existing.data = json.dumps(to_store)
	except TypeError:
		raise HTTPException(status_code=500, detail="Failed to serialize profile data to JSON")

	db.commit()

	# Return 204 No Content for successful update
	return Response(status_code=204)