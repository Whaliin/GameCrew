from typing import Any, ClassVar, Literal, List, Annotated, get_args, get_origin

from pydantic import BaseModel, Field

# Pydantic schemas for database game profile models.
# The base class for all schemas is GameProfileSpec, which can be extended with additional fields.
class GameProfileSpec(BaseModel):
	# Default fields that all game profile schemas should have.
	game_name: ClassVar[str]
	game_slug: ClassVar[str]
	DISPLAY_FIELD: ClassVar[str | None] = None

	# Override the __init_subclass__ method to enforce that all subclasses implement
	# the validate_schema method and have game_slug and game_name fields.
	def __init_subclass__(cls, **kwargs):
		super().__init_subclass__(**kwargs)
		if not hasattr(cls, "game_slug") or not hasattr(cls, "game_name"):
			raise NotImplementedError(f"{cls.__name__} must have game_slug and game_name fields")

	@classmethod
	def _strip_optional(cls, annotation: Any) -> Any:
		"""Unwrap Optional[T] style annotations and return the inner type."""
		# Pydantic and typing both wrap optional values in unions / Annotated layers.
		# This helper peels those layers away so the rest of the code can inspect the real field type.
		origin = get_origin(annotation)
		
		# If it's an Annotated type (which can include validation metadata),
		# we want to look at the underlying type for validation purposes.
		# We do this by recursively stripping away the Annotated wrapper until we get to the base type.
		if origin is Annotated:
			return cls._strip_optional(get_args(annotation)[0])
		
		# When you define a field like this: field: str | None
		# It becomes an annotation of type Union[str, NoneType], which is how Optional[str] is represented internally.
		# You can also define it like this: field: Optional[str] (which is the same thing). 
		# In either case, we want to extract the T from Optional[T] so we can work with the real type.
		# We check if the annotation is a Union that includes None, and if so,
		# Remove the None branch so the rest of the logic can work with the real field type.
		args = get_args(annotation)
		# If it's not a Union or doesn't include None, we just return the original annotation.
		if origin is None or not args:
			return annotation

		# If it's a Union that includes None, we want to extract the non-None type.
		non_none_args = [arg for arg in args if arg is not type(None)]
		# If we found more than one non-None type, it's not a simple Optional[T],
		# so we return the original annotation to avoid breaking complex unions.
		if len(non_none_args) == 1:
			return cls._strip_optional(non_none_args[0])
		return annotation

	@classmethod
	def _field_validation_metadata(cls, field) -> dict[str, object]:
		"""Derive UI metadata from a Pydantic field annotation and its Field metadata."""
		# Build the frontend metadata directly from the field definition.
		# This keeps the UI in sync with the schema without maintaining a second rule source.
		rules: dict[str, object] = {}
		
		# Get the annotation for the field, which may include type and validation info. If no annotation, return empty rules.
		annotation = getattr(field, "annotation", None)
		if annotation is None:
			return rules

		# Strip Optional/Annotated wrappers so we can inspect the base type and any metadata cleanly.
		annotation = cls._strip_optional(annotation)

		# First, extract any explicit validation rules from the Field metadata (like max_length, ge, le, etc).
		metadata_items = list(getattr(field, "metadata", []) or [])

		# If the field uses Pydantic's Field, it may have validation constraints defined there.
		# We loop through the metadata items to find these constraints and add them to the rules dict.
		for meta in metadata_items:
			# Field metadata carries length and range constraints that the frontend can reuse.
			for attr_name, rule_name in (("max_length", "max_length"), ("min_length", "min_length"), ("ge", "min"), ("le", "max")):
				# Check if this metadata item has the relevant attribute (e.g. max_length) and if so, add it to the rules dict under a standardized name.
				value = getattr(meta, attr_name, None)
				if value is not None:
					# Only set the rule if it's not already set by an earlier metadata item, to allow Field() to override defaults.
					rules.setdefault(rule_name, value)

		# Next, we inspect the type annotation itself for additional validation info,
		# such as allowed values from Literals or whether it's a multi-select list.
		origin = get_origin(annotation)
		# If the field is a Literal (i.e. a fixed set of allowed values),
		# we add those allowed values to the rules dict so the frontend can render a select input.
		if origin is Literal:
			# Literal fields become select-style controls with a fixed allowed value list.
			rules["allowedvalues"] = list(get_args(annotation))
		# If the field is a list of Literals, we treat it as a multi-select control with a fixed allowed value list.
		elif origin in (list, List):
			# A list of Literals means the UI should allow multi-select for that field.
			inner = get_args(annotation)[0] if get_args(annotation) else None
			inner = cls._strip_optional(inner)
			if get_origin(inner) is Literal:
				rules["allowedvalues"] = list(get_args(inner))
				rules["multi"] = True

		return rules

	@classmethod
	def to_form_schema(cls):
		"""Helper method to convert a GameProfileSpec subclass into a schema that can be used for form generation on the frontend."""
		# Build field-level metadata directly from Pydantic annotations.
		fields = {}
		for field_name, field in cls.model_fields.items():
			rules = cls._field_validation_metadata(field)
			fields[field_name] = {
				"type": str(getattr(field, "annotation", "unknown")),
				"validation": rules,
			}
		return {"game_name": cls.game_name, "game_slug": cls.game_slug, "fields": fields, "display_field": cls.DISPLAY_FIELD}

	@classmethod
	def get_schema(cls, typename: str) -> type | None:
		"""Helper method to get a GameProfileSpec subclass based on the typename."""
		return next((subclass for subclass in cls.__subclasses__() if subclass.__name__ == typename), None)

	@classmethod
	def get_display_field(cls) -> str | None:
		"""Return the schema field that should be shown on cards for this game."""
		return cls.DISPLAY_FIELD

	@classmethod
	def get_display_value(cls, profile_data: dict[str, object]) -> object | None:
		"""Return the value that should be shown on a card for this schema."""
		display_field = cls.get_display_field()
		if display_field and display_field in profile_data:
			return profile_data.get(display_field)
		# Keep the legacy fallback so games without a configured display field still show something useful.
		return profile_data.get("rank") or profile_data.get("premier_rank")
	
class CounterStrikeSpec(GameProfileSpec):
	game_name = "Counter-Strike 2"
	game_slug = "cs2"
	DISPLAY_FIELD = "premier_rank"

	premier_rank: Literal[
		"Unranked",
		"0-5k",
		"5k-10k",
		"10k-15k",
		"15k-20k",
		"20k-25k",
		"25k-30k",
		"30k+",
	] | None = None
	role: Literal["Entry Fragger", "Support", "AWPer", "In-Game Leader", "Lurker"] | None = None
	
class LeagueOfLegendsSpec(GameProfileSpec):
	game_name = "League of Legends"
	game_slug = "league-of-legends"
	DISPLAY_FIELD = "rank"

	rank: Literal["Iron", "Bronze", "Silver", "Gold", "Platinum", "Diamond", "Master", "Grandmaster", "Challenger"] | None = None
	main_role: Literal["Top", "Jungle", "Mid", "ADC", "Support"] | None = None
	
class ValorantSpec(GameProfileSpec):
	game_name = "Valorant"
	game_slug = "valorant"
	DISPLAY_FIELD = "rank"

	rank: Literal["Iron", "Bronze", "Silver", "Gold", "Platinum", "Diamond", "Immortal", "Radiant"] | None = None
	main_agent: Annotated[str, Field(max_length=50)] | None = None

class ApexLegendsSpec(GameProfileSpec):
	game_name = "Apex Legends"
	game_slug = "apex-legends"
	DISPLAY_FIELD = "rank"

	rank: Literal["Bronze", "Silver", "Gold", "Platinum", "Diamond", "Master", "Apex Predator"] | None = None
	main_legend: Annotated[str, Field(max_length=50)] | None = None

class ArcRaidersSpec(GameProfileSpec):
	game_name = "Arc Raiders"
	game_slug = "arc-raiders"
	DISPLAY_FIELD = "rank"

	rank: Literal["Bronze", "Silver", "Gold", "Platinum", "Diamond", "Master", "Grandmaster"] | None = None
	main_hero: Annotated[str, Field(max_length=50)] | None = None

class MobileLegendsSpec(GameProfileSpec):
	game_name = "Mobile Legends"
	game_slug = "mobile-legends"
	DISPLAY_FIELD = "rank"

	rank: Literal["Warrior", "Elite", "Master", "Grandmaster", "Epic", "Legend", "Mythic", "Mythical Immortal"] | None = None
	main_hero: Annotated[str, Field(max_length=50)] | None = None

class MinecraftSpec(GameProfileSpec):
	game_name = "Minecraft"
	game_slug = "minecraft"
	DISPLAY_FIELD = "preferred_mode"

	preferred_mode: Literal["Survival", "Creative", "Adventure", "Spectator"] | None = None
	favorite_mod: Annotated[str, Field(max_length=100)] | None = None

class PUBGSpec(GameProfileSpec):
	game_name = "PUBG: Battlegrounds"
	game_slug = "pubg"
	DISPLAY_FIELD = "rank"

	rank: Literal["Bronze", "Silver", "Gold", "Platinum", "Diamond", "Master", "Grandmaster"] | None = None
	main_weapon: Annotated[str, Field(max_length=50)] | None = None

class CallOfDutySpec(GameProfileSpec):
	game_name = "Call of Duty: Warzone"
	game_slug = "call-of-duty-warzone"
	DISPLAY_FIELD = "preferred_mode"

	main_weapon: Annotated[str, Field(max_length=50)] | None = None
	preferred_mode: Literal["Battle Royale", "Plunder", "Resurgence"] | None = None

class RustSpec(GameProfileSpec):
	game_name = "Rust"
	game_slug = "rust"
	DISPLAY_FIELD = "playstyle"

	playstyle: Literal["Solo", "Duo", "Squad"] | None = None
	main_weapon: Annotated[str, Field(max_length=50)] | None = None

class EscapeFromTarkovSpec(GameProfileSpec):
	game_name = "Escape From Tarkov"
	game_slug = "escape-from-tarkov"
	DISPLAY_FIELD = "playstyle"

	faction: Literal["USEC", "BEAR", "Scav"] | None = None
	main_weapon: Annotated[str, Field(max_length=50)] | None = None
	playstyle: Literal["Aggressive", "Stealthy", "Balanced"] | None = None

class Dota2Spec(GameProfileSpec):
	game_name = "Dota 2"
	game_slug = "dota-2"
	DISPLAY_FIELD = "rank"

	rank: Literal["Herald", "Guardian", "Crusader", "Archon", "Legend", "Ancient", "Divine", "Immortal"] | None = None

class GTAVSpec(GameProfileSpec):
	game_name = "GTA V"
	game_slug = "gta-v"
	DISPLAY_FIELD = "preferred_mode"

	preferred_mode: Literal["Story Mode", "Online Freemode", "Online Heists", "Online Races", "Online Other"] | None = None
	main_activity: Annotated[str, Field(max_length=100)] | None = None

class RobloxSpec(GameProfileSpec):
	game_name = "Roblox"
	game_slug = "roblox"
	DISPLAY_FIELD = "preferred_genre"

	favorite_game: Annotated[str, Field(max_length=100)] | None = None
	preferred_genre: Literal["Adventure", "Roleplay", "Simulator", "Obby", "Tycoon", "FPS", "Horror", "Other"] | None = None

class OverwatchSpec(GameProfileSpec):
	game_name = "Overwatch 2"
	game_slug = "overwatch-2"
	DISPLAY_FIELD = "rank"

	rank: Literal["Bronze", "Silver", "Gold", "Platinum", "Diamond", "Master", "Grandmaster", "Top 500"] | None = None
	main_hero: Annotated[str, Field(max_length=50)] | None = None

class WorldOfWarcraftSpec(GameProfileSpec):
	game_name = "World of Warcraft"
	game_slug = "world-of-warcraft"
	DISPLAY_FIELD = "main_class"

	main_class: Literal["Warrior", "Paladin", "Hunter", "Rogue", "Priest", "Death Knight", "Shaman", "Mage", "Warlock", "Monk", "Druid", "Demon Hunter"] | None = None
	main_role: Literal["Tank", "Healer", "DPS"] | None = None

class MarvelRivalsSpec(GameProfileSpec):
	game_name = "Marvel Rivals"
	game_slug = "marvel-rivals"

class FIFASpec(GameProfileSpec):
	game_name = "FIFA"
	game_slug = "fifa"

class DiabloSpec(GameProfileSpec):
	game_name = "Diablo IV"
	game_slug = "diablo-iv"
	DISPLAY_FIELD = "main_class"
	main_class: Literal["Barbarian", "Druid", "Necromancer", "Rogue", "Sorcerer"] | None = None
	playstyle: Literal["Solo", "Duo", "Squad"] | None = None

class EldenRingSpec(GameProfileSpec):
	game_name = "Elden Ring"
	game_slug = "elden-ring"
	DISPLAY_FIELD = "main_class"

	main_class: Literal["Vagabond", "Warrior", "Hero", "Bandit", "Astrologer", "Prophet", "Samurai", "Prisoner", "Confessor", "Wretch"] | None = None
	playstyle: Literal["Melee", "Ranged", "Magic", "Stealth"] | None = None

class GenshinImpactSpec(GameProfileSpec):
	game_name = "Genshin Impact"
	game_slug = "genshin-impact"
	DISPLAY_FIELD = "preferred_role"

	main_character: Annotated[str, Field(max_length=50)] | None = None
	preferred_role: Literal["DPS", "Support", "Healer", "Sub-DPS"] | None = None

class FortniteSpec(GameProfileSpec):
	game_name = "Fortnite"
	game_slug = "fortnite"
	DISPLAY_FIELD = "preferred_mode"

	preferred_mode: Literal["Solo", "Duo", "Squad"] | None = None
	main_weapon: Annotated[str, Field(max_length=50)] | None = None