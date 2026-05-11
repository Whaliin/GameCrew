import json
from datetime import datetime
from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Game, Player, PlayerGameProfile, PlayerProfile
from app.routers.api.players import map_age_range
from app.schemas import GameProfileSpec

router = APIRouter(prefix="/api/search", tags=["search"])


class PlayerSearchRequest(BaseModel):
	model_config = ConfigDict(extra="forbid")

	name_contains: str | None = None
	age_lo: int | None = None
	age_hi: int | None = None
	playtime: list[str] = Field(default_factory=list)
	platform: list[str] = Field(default_factory=list)
	language: list[str] = Field(default_factory=list)
	schema_filters: dict[str, Any] = Field(default_factory=dict)

def _normalize_values(value: Any) -> list[str]:
	"""
	Normalize the input value into a list of strings for consistent matching. This allows the matching logic to treat single values and lists uniformly.

	:param Any value: The input value which can be None, a single value, or a list/tuple of values.
	:return: A list of strings representing the normalized values. If the input is None or an empty string, an empty list is returned.
	"""
	# Empty list
	if value is None:
		return []
	# If list, convert all items to strings and filter out None or empty values
	if isinstance(value, list):
		return [str(item) for item in value if item not in (None, "")]
	
	# If tuple, convert to list and apply the same logic
	if isinstance(value, tuple):
		return [str(item) for item in value if item not in (None, "")]
	
	# If string is empty, return empty list
	if value == "":
		return []
	return [str(value)]

def _matches_rule_value(actual_value: Any, selected_value: Any, rules: dict[str, Any]) -> bool:
	"""
	Check if the actual value matches the selected value(s) based on the rules defined in the schema.

	:param Any actual_value: The value from the player's profile (can be a single value or a list of values).
	:param Any selected_value: The value(s) selected in the search filter (can be a single value or a list of values).
	:param dict[str, Any] rules: Validation rules from the schema for this field (e.g., whether it's multi-select).

	:return: True if there is a match according to the rules, False otherwise.
	"""
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

# Check if the profile data matches the schema filters. If a filter is not present for a field, it is considered a match.
# If a filter is present, the value must match according to the rules defined in the schema for that field.
def _parse_profile_data(raw_data: str | None) -> dict[str, object]:
	"""
	Parse the raw JSON profile data for a player's game profile. If there is no data or if the data is not valid JSON, return an empty dict.

	:param str | None raw_data: The raw JSON string from the PlayerGameProfile.data field.
	:return: A dictionary of the parsed profile data, or an empty dict if there is no data or if the data is invalid.
	"""
	# If there is no data, return an empty dict. If the data is not valid JSON, also return an empty dict.
	if not raw_data:
		return {}
	try:
		parsed = json.loads(raw_data)
	except (ValueError, TypeError):
		return {}
	return parsed if isinstance(parsed, dict) else {}

@router.post("/games/{game_slug}/players")
def search_players_for_game(
	game_slug: str,
	search_request: PlayerSearchRequest,
	limit: int = 50,
	db: Session = Depends(get_db),
):
	"""
	Search for player profiles based on the specified criteria for a given game.

	:param str game_slug: The slug identifier for the game to search within.
	:param PlayerSearchRequest search_request: The search criteria including age range, playtime, platform, language, and any game-specific schema filters.
	:param int limit: The maximum number of results to return (default is 50, max is 50).
	:return: A JSON response containing the list of matching player profiles and any relevant metadata.
	:raises HTTPException: 404 if the game is not found, 422 if the search criteria are invalid.
	"""
	# Clamp the limit to a reasonable number to prevent abuse.
	limit = max(1, min(limit, 50))

	# Log the schema filters
	if search_request.schema_filters:
		print(f"Received schema filters for game '{game_slug}': {search_request.schema_filters}")

	"""Search for player profiles based on the specified criteria for a given game."""
	current_year = datetime.now().year

	# Get the game
	game = db.query(Game).filter(Game.slug == game_slug).first()
	if not game:
		raise HTTPException(status_code=404, detail="Game not found")

	schema_class = GameProfileSpec.get_schema(game.schema_spec) if game.schema_spec else None
	schema_fields = schema_class.to_form_schema()["fields"] if schema_class else {}

	# Check if the profile data matches the schema filters. If a filter is not present for a field, it is considered a match.
	# If a filter is present, the value must match according to the rules defined in the schema for that field.
	def _matches_schema_field(profile_data: dict[str, object], field_name: str) -> bool:
		rules = schema_fields.get(field_name, {}).get("validation", {})
		if field_name not in search_request.schema_filters:
			return True
		return _matches_rule_value(profile_data.get(field_name), search_request.schema_filters.get(field_name), rules)
	
	game_schema = GameProfileSpec.get_schema(game.schema_spec) if game.schema_spec else None

	# Get the player profiles matching the search criteria for this game.
	player_rows = (
		db.query(Player, PlayerProfile, PlayerGameProfile)
		.join(PlayerProfile, PlayerProfile.player_id == Player.id)
		.join(PlayerGameProfile, PlayerGameProfile.player_id == Player.id)
		.filter(PlayerGameProfile.game_id == game.id)
	)

	# filter player rows by name_contains if specified
	if search_request.name_contains:
		player_rows = player_rows.filter(Player.username.ilike(f"%{search_request.name_contains}%"))

	# convert player rows to a list
	player_rows = player_rows.all()


	results: list[dict[str, object]] = []
	for player, profile, game_profile in player_rows:
		age = current_year - profile.birth_year if profile.birth_year else None
		
		profile_data = _parse_profile_data(game_profile.data)

		# Convert the profile data into the game spec class so we can get the display value (this also has the side effect of validating the data)
		try:
			profile_schema = game_schema(**profile_data) if game_schema else None
		except Exception:
			continue  # If the data is invalid according to the schema, skip this profile

		# Filter by age range if specified
		if search_request.age_lo is not None and (age is None or age < search_request.age_lo):
			continue
		if search_request.age_hi is not None and (age is None or age > search_request.age_hi):
			continue

		# Filter by playtime
		if search_request.playtime and not _matches_rule_value([item.name for item in player.playtimes], search_request.playtime, {}):
			continue

		# Filter by platform
		if search_request.platform and not _matches_rule_value([item.name for item in player.platforms], search_request.platform, {}):
			continue

		# Filter by language
		if search_request.language and not _matches_rule_value([item.name for item in player.languages], search_request.language, {}):
			continue

		# Filter by schema fields
		if not all(_matches_schema_field(profile_data, field_name) for field_name in schema_fields.keys()):
			continue

		# Append the result with profile information.
		results.append(
			{
				"username": player.username,
				"avatar_url": "/static/img/profiles/default.jpg",
				"age": map_age_range(profile.birth_year) if profile.birth_year else "Unknown",
				"display_value": profile_schema.get_display_value(profile_data) if profile_schema else None,
				"platform": ", ".join(item.name for item in player.platforms) or None,
				"playtime": ", ".join(item.name for item in player.playtimes) or None,
				"languages": ", ".join(item.name for item in player.languages) or None,
				"discord": profile.discord,
				"bio": profile.bio,
			}
		)

	return {
		"game_slug": game_slug,
		"results": results[:limit],
		"meta": {
			"schema_fields": list(schema_fields.keys()),
		},
	}

