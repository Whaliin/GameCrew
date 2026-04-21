from fastapi import APIRouter, HTTPException

router = APIRouter(prefix="/api/games", tags=["games"])


GAMES_CATALOG: list[dict[str, str]] = [
	{"slug": "cs2", "display_name": "Counter-Strike 2"},
	{"slug": "lol", "display_name": "League of Legends"},
	{"slug": "valorant", "display_name": "Valorant"},
	{"slug": "arcraiders", "display_name": "ARC Raiders"},
	{"slug": "mobilelegends", "display_name": "Mobile Legends"},
]

@router.get("/")
def list_games():
	return HTTPException(
		status_code=501,
		detail="TODO: return list of games with basic metadata (slug, display name, image URL)",
	)


@router.get("/{game_slug}")
def get_game(game_slug: str):
	return HTTPException(
			status_code=501,
			detail=f"TODO: return details for game with slug '{game_slug}'",
		)
