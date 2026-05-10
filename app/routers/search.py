import ast
from datetime import datetime
from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Game, Player, PlayerGameProfile, PlayerProfile
from app.schemas import GameProfileSpec

router = APIRouter(prefix="/api/search", tags=["search"])


class PlayerSearchRequest(BaseModel):
	model_config = ConfigDict(extra="forbid")

	age_lo: int | None = None
	age_hi: int | None = None
	playtime: list[str] = Field(default_factory=list)
	platform: list[str] = Field(default_factory=list)
	language: list[str] = Field(default_factory=list)
	rank: list[str] = Field(default_factory=list)
	schema_filters: dict[str, Any] = Field(default_factory=dict)

# TODO: Add response_model for search results list payload once endpoint is implemented.
@router.post("/games/{game_slug}/players")
def search_players_for_game(
	game_slug: str,
	search_request: PlayerSearchRequest,
	db: Session = Depends(get_db),
):
	"""Search for player profiles based on the specified criteria for a given game."""
	current_year = datetime.now().year

	# Get the game
	game = db.query(Game).filter(Game.slug == game_slug).first()
	if not game:
		raise HTTPException(status_code=404, detail="Game not found")

	schema_class = GameProfileSpec.get_schema(game.schema_spec) if game.schema_spec else None
	validation_rules = schema_class.VALIDATION_RULES if schema_class else {}
	rank_field_name = (
		"rank"
		if "rank" in validation_rules
		else next((field_name for field_name in validation_rules if "rank" in field_name), None)
	)

	def _normalize_values(value: Any) -> list[str]:
		if value is None:
			return []
		if isinstance(value, list):
			return [str(item) for item in value if item not in (None, "")]
		if isinstance(value, tuple):
			return [str(item) for item in value if item not in (None, "")]
		if value == "":
			return []
		return [str(value)]

	def _matches_rule_value(actual_value: Any, selected_value: Any, rules: dict[str, Any]) -> bool:
		selected_values = _normalize_values(selected_value)
		if not selected_values:
			return True

		if actual_value is None:
			return False

		if rules.get("multi", False):
			actual_values = _normalize_values(actual_value)
			actual_lookup = {value.lower() for value in actual_values}
			return any(value.lower() in actual_lookup for value in selected_values)

		if isinstance(actual_value, list):
			actual_values = _normalize_values(actual_value)
			actual_lookup = {value.lower() for value in actual_values}
			return any(value.lower() in actual_lookup for value in selected_values)

		return str(actual_value).lower() in {value.lower() for value in selected_values}

	def _parse_profile_data(raw_data: str | None) -> dict[str, object]:
		if not raw_data:
			return {}
		try:
			parsed = ast.literal_eval(raw_data)
		except (ValueError, SyntaxError):
			return {}
		return parsed if isinstance(parsed, dict) else {}

	def _matches_schema_field(profile_data: dict[str, object], field_name: str) -> bool:
		rules = validation_rules.get(field_name, {})
		if field_name not in search_request.schema_filters:
			return True
		return _matches_rule_value(profile_data.get(field_name), search_request.schema_filters.get(field_name), rules)
	
	# Get the player profiles matching the search criteria for this game.
	player_rows = (
		db.query(Player, PlayerProfile, PlayerGameProfile)
		.join(PlayerProfile, PlayerProfile.player_id == Player.id)
		.join(PlayerGameProfile, PlayerGameProfile.player_id == Player.id)
		.filter(PlayerGameProfile.game_id == game.id)
		.all()
	)

	results: list[dict[str, object]] = []
	for player, profile, game_profile in player_rows:
		age = current_year - profile.birth_year if profile.birth_year else None
		profile_data = _parse_profile_data(game_profile.data)
		if search_request.age_lo is not None and (age is None or age < search_request.age_lo):
			continue
		if search_request.age_hi is not None and (age is None or age > search_request.age_hi):
			continue

		if search_request.playtime and not _matches_rule_value([item.name for item in player.playtimes], search_request.playtime, {}):
			continue
		if search_request.platform and not _matches_rule_value([item.name for item in player.platforms], search_request.platform, {}):
			continue
		if search_request.language and not _matches_rule_value([item.name for item in player.languages], search_request.language, {}):
			continue

		if search_request.rank and rank_field_name:
			stored_rank = profile_data.get(rank_field_name)
			if not _matches_rule_value(stored_rank, search_request.rank, validation_rules.get(rank_field_name, {})):
				continue

		if not all(_matches_schema_field(profile_data, field_name) for field_name in validation_rules.keys()):
			continue

		results.append(
			{
				"username": player.username,
				"avatar_url": "/static/img/profiles/default.jpg",
				"age": age,
				"rank": profile_data.get("rank") or profile_data.get("premier_rank"),
				"platform": ", ".join(item.name for item in player.platforms) or None,
				"playtime": ", ".join(item.name for item in player.playtimes) or None,
				"languages": ", ".join(item.name for item in player.languages) or None,
				"discord": profile.discord,
				"bio": profile.bio,
			}
		)

	return {
		"game_slug": game_slug,
		"results": results,
		"meta": {
			"schema_fields": list(validation_rules.keys()),
		},
	}

