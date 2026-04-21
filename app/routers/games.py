from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy.orm import Session

from app.auth.sessions import get_current_user
from app.database import get_db
from app.models import Game, PlayerGameFavorites

router = APIRouter(prefix="/api/games", tags=["games"])

# TODO: Add response_model=list[schemas.Game] once output shape is finalized.
@router.get("/")
def list_games(search: str | None = Query(default=None), db: Session = Depends(get_db)):
	# Return all games by default, or filter by partial name match.
	query = db.query(Game)
	if search:
		search_term = search.strip().strip('"')
		if search_term:
			query = query.filter(Game.name.ilike(f"%{search_term}%"))

	games = query.all()

	return games

# TODO: Add response_model=schemas.Game when detail endpoint contract is finalized.
@router.get("/{game_slug}")
def get_game(game_slug: str, db: Session = Depends(get_db)):
	game = db.query(Game).filter(Game.slug == game_slug).first()
	if game is None:
		raise HTTPException(status_code=404, detail="Game not found")
	return game

@router.post("/{game_slug}/favorite")
def favorite_game(request: Request, game_slug: str, db: Session = Depends(get_db)):
	# User favorites a game
	game = db.query(Game).filter(Game.slug == game_slug).first()
	if game is None:
		raise HTTPException(status_code=404, detail="Game not found")
	
	user = get_current_user(request)
	if user is None:
		raise HTTPException(status_code=401, detail="Authentication required")
	
	try:
		# add a new row to the PlayerGameFavorites table
		db.add(PlayerGameFavorites(player_id=user.player_id, game_id=game.id))
		db.commit()
		return {"message": f"Game '{game.name}' favorited successfully."}
	except Exception as e:
		db.rollback()
		raise HTTPException(status_code=500, detail="Failed to favorite game") from e