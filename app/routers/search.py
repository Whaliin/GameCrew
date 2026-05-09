from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db

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
	"""Search for player profiles based on the specified criteria for a given game."""

	raise HTTPException(status_code=501, detail="Search endpoint not implemented yet")

	#return {"game_slug": game_slug, "results": []}
