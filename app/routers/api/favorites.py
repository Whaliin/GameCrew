"""Endpoints for managing the current user's favorite games."""

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from app.auth.sessions import get_optional_user
from app.database import get_db
from app.models import Game, PlayerGameProfile

router = APIRouter(prefix="/api/me/favorites", tags=["favorites"])


def require_user(request: Request):
	"""Local helper — returns the session or 401 (no redirect, since this is JSON)."""
	user = get_optional_user(request)
	if user is None:
		raise HTTPException(status_code=401, detail="Not authenticated")
	return user


@router.get("")
def list_my_favorites(
	request: Request,
	db: Session = Depends(get_db),
):
	"""Return slugs of all games the current user has favorited."""
	user = require_user(request)

	rows = (
		db.query(Game.slug)
		.join(PlayerGameProfile, PlayerGameProfile.game_id == Game.id)
		.filter(PlayerGameProfile.player_id == user.player_id)
		.all()
	)
	return {"slugs": [row.slug for row in rows]}


@router.put("/{slug}")
def add_favorite(
	slug: str,
	request: Request,
	db: Session = Depends(get_db),
):
	"""Mark a game as favorite for the current user."""
	user = require_user(request)

	game = db.query(Game).filter(Game.slug == slug).first()
	if game is None:
		raise HTTPException(status_code=404, detail="Game not found")

	# Already favorited? — no-op, return ok
	existing = (
		db.query(PlayerGameProfile)
		.filter(
			PlayerGameProfile.player_id == user.player_id,
			PlayerGameProfile.game_id == game.id,
		)
		.first()
	)
	if existing is None:
		db.add(PlayerGameProfile(player_id=user.player_id, game_id=game.id))
		db.commit()

	return {"ok": True, "slug": slug}


@router.delete("/{slug}")
def remove_favorite(
	slug: str,
	request: Request,
	db: Session = Depends(get_db),
):
	"""Remove a game from the current user's favorites."""
	user = require_user(request)

	game = db.query(Game).filter(Game.slug == slug).first()
	if game is None:
		raise HTTPException(status_code=404, detail="Game not found")

	db.query(PlayerGameProfile).filter(
		PlayerGameProfile.player_id == user.player_id,
		PlayerGameProfile.game_id == game.id,
	).delete()
	db.commit()

	return {"ok": True, "slug": slug}