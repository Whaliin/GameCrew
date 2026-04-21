from fastapi import APIRouter, HTTPException, Query

router = APIRouter(prefix="/api/search", tags=["search"])

# TODO: Add response_model for search results list payload once endpoint is implemented.
@router.get("/games/{game_slug}/players")
def search_players_for_game(game_slug: str, q: str = Query(default="")):
	raise HTTPException(
		status_code=501,
		detail=f"TODO: search players for game '{game_slug}' using query '{q}'",
	)
