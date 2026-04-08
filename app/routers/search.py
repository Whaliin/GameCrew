from fastapi import APIRouter, HTTPException, Query

router = APIRouter(prefix="/api/search", tags=["search"])


def get_search_scope_stub() -> str:
	"""Return the currently supported search scope."""
	return "per-game-only"


@router.get("/games/{game_slug}/players")
def search_players_for_game_stub(game_slug: str, q: str = Query(default="")):
	raise HTTPException(
		status_code=501,
		detail=f"TODO: search players for game '{game_slug}' using query '{q}'",
	)
