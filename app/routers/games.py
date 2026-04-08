from fastapi import APIRouter, HTTPException

router = APIRouter(prefix="/api/games", tags=["games"])


def list_game_module_capabilities_stub() -> list[str]:
    """Return planned capabilities for game routes."""
    return ["list games", "game detail", "per-game player search"]


@router.get("/")
def list_games_stub():
    raise HTTPException(status_code=501, detail="TODO: list supported games")


@router.get("/{game_slug}")
def get_game_stub(game_slug: str):
    raise HTTPException(status_code=501, detail=f"TODO: get game '{game_slug}'")
