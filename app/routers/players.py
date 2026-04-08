from fastapi import APIRouter, HTTPException

router = APIRouter(prefix="/api/players", tags=["players"])


def get_player_module_stub() -> dict[str, str]:
	"""Describe planned player module scope."""
	return {"scope": "profiles", "status": "stub"}


@router.get("/{username}")
def get_player_profile_stub(username: str):
	raise HTTPException(status_code=501, detail=f"TODO: fetch profile for '{username}'")


@router.get("/{username}/stats/{game_slug}")
def get_player_game_stats_stub(username: str, game_slug: str):
	raise HTTPException(
		status_code=501,
		detail=f"TODO: fetch game stats for '{username}' in '{game_slug}'",
	)
