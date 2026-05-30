"""
Page route for displaying game details and player search functionality.
"""

import json

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.auth.sessions import get_user
from app.models import Game, PlayerGameProfile, Playtime, Platform, Language
from app.routers.pages._shared import templates, create_profile_context
from app.schemas import GameProfileSpec
from app.utils.assets import get_game_image_url


router = APIRouter(prefix="/game", tags=["pages"])


AGE_MARK_LABELS: list[str] = ["18", "25", "35", "45", "45+"]

@router.get("/{game_slug}", response_class=HTMLResponse)
def game_page(request: Request, game_slug: str, db: Session = Depends(get_db)):
	"""Get a game-specific page with details and player search."""
	context = {}

	# get the game info
	game = db.query(Game).filter(Game.slug == game_slug).first()
	if not game:
		raise HTTPException(status_code=404, detail="Game not found")
	
	user = get_user(request, db)
	
	context["game"] = {
		"name": game.name,
		"slug": game.slug,
		"image_url": get_game_image_url(game.slug),
		"is_favorite": db.query(PlayerGameProfile).filter(PlayerGameProfile.game_id == game.id, PlayerGameProfile.player_id == user.id).first() is not None if user else False
	}

	context["age_marks"] = AGE_MARK_LABELS

	game_schema = GameProfileSpec.get_schema(game.schema_spec)
	# attach filter options
	context["filter_options"] = {
		"playtimes": [pt.name for pt in db.query(Playtime).distinct()],
		"platforms": [pf.name for pf in db.query(Platform).distinct()],
		"languages": [lang.name for lang in db.query(Language).distinct()],
		"filter_specs": {
			field_name: field_spec["validation"]
			for field_name, field_spec in game_schema.to_form_schema()["fields"].items()
		} if game_schema else {}
	}

	# If this game has a schema, expose rank options and current user rank for the frontend popup
	if game_schema:
		# Build a lightweight form schema and pull the display field + allowed values (if any)
		try:
			form_schema = game_schema.to_form_schema()
			display_field = form_schema.get("display_field")
			options = []
			if display_field:
				field_meta = form_schema.get("fields", {}).get(display_field, {})
				options = field_meta.get("validation", {}).get("allowedvalues") or []
			context["rank_display_field"] = display_field
			context["rank_options_json"] = json.dumps(options)
			context["rank_display_field_json"] = json.dumps(display_field) if display_field is not None else json.dumps(None)
		except Exception:
			context["rank_display_field"] = None
			context["rank_options_json"] = json.dumps([])

	# Determine current user's rank display value (if logged in and profile exists)
	user = get_user(request, db)
	user_rank = None
	game_profile_data = {}
	if user and game_schema:
		pgp = db.query(PlayerGameProfile).filter(PlayerGameProfile.game_id == game.id, PlayerGameProfile.player_id == user.id).first()
		if pgp and pgp.data:
			try:
				game_profile_data = json.loads(pgp.data)
				user_rank = game_schema.get_display_value(game_profile_data)
			except Exception:
				user_rank = None

		# Provide full form schema and current profile data for server-rendered modal (combobox-only)
		try:
			form_schema = game_schema.to_form_schema()
			context["game_form_schema"] = form_schema
			# attach parsed profile data (dict) for pre-selecting options
			context["game_profile_data"] = game_profile_data
		except Exception:
			context["game_form_schema"] = None
			context["game_profile_data"] = {}
	context["user_rank"] = user_rank
	context["user_rank_json"] = json.dumps(user_rank) if user_rank is not None else json.dumps(None)

	context["profile"] = create_profile_context(db, request)
	context["theme"] = context["profile"]["theme"] if context["profile"] else "dark"

	return templates.TemplateResponse(request=request, name="game.html", context=context)