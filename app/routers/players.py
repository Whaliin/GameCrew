from fastapi import APIRouter, HTTPException

router = APIRouter(prefix="/api/players", tags=["players"])

@router.get("/{username}")
def get_player_profile(username: str):
	raise HTTPException(status_code=501, detail=f"TODO: fetch profile for '{username}'")


@router.get("/{username}/stats/{game_slug}")
def get_player_game_stats(username: str, game_slug: str):
	raise HTTPException(
		status_code=501,
		detail=f"TODO: fetch game stats for '{username}' in '{game_slug}'",
	)
