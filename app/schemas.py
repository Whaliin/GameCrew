from typing import ClassVar

from pydantic import BaseModel

# Pydantic schemas for database game profile models.
# The base class for all schemas is GameProfileSpec, which can be extended with additional fields.
class GameProfileSpec(BaseModel):
	# Default fields that all game profile schemas should have.
	game_name: ClassVar[str]
	game_slug: ClassVar[str]

	VALIDATION_RULES: ClassVar[dict[str, dict[str, object]]] = {}

	# Override the __init_subclass__ method to enforce that all subclasses implement
	# the validate_schema method and have game_slug and game_name fields.
	def __init_subclass__(cls, **kwargs):
		super().__init_subclass__(**kwargs)
		if not hasattr(cls, "validate_schema"):
			raise NotImplementedError(f"{cls.__name__} must implement a validate_schema() method")
		if not hasattr(cls, "game_slug") or not hasattr(cls, "game_name"):
			raise NotImplementedError(f"{cls.__name__} must have game_slug and game_name fields")

	@classmethod
	def to_form_schema(cls):
		"""Helper method to convert a GameProfileSpec subclass into a schema that can be used for form generation on the frontend."""
		return {
			# Include the game name and slug for reference on the frontend.
			"game_name": cls.game_name,
			"game_slug": cls.game_slug,
			"fields": {
				field_name: {
					# Get the type annotation for the field (e.g int, str) or default to unknown.
					"type": getattr(field, "annotation", "unknown"),
					# Get any validation rules for the field from the VALIDATION_RULES dict.
					"validation": cls.VALIDATION_RULES.get(field_name, {})
					#"optional": True
				}
				for field_name, field in cls.model_fields.items()
			}
		}
	
	@classmethod
	def get_schema(cls, typename: str) -> type | None:
		"""Helper method to get a GameProfileSpec subclass based on the typename."""
		return next((subclass for subclass in cls.__subclasses__() if subclass.__name__ == typename), None)
	
	def _validate_field_value(self, value, rules) -> bool:
		"""Helper method to validate a single field value against its rules.
		Every rule is optional, so only the specified rules will be checked.
			- min: the value must be greater than or equal to this (for numeric fields)
			- max: the value must be less than or equal to this (for numeric fields)
			- allowedvalues: the value must be one of these (for string or numeric fields)
			- min_length: the string value must have at least this many characters (for string fields)
			- max_length: the string value must have at most this many characters (for string fields)
		"""
		if "min" in rules and value < rules["min"]:
			return False
		if "max" in rules and value > rules["max"]:
			return False
		
		# Check that the value is one of the allowed values (if specified)
		if "allowedvalues" in rules and value not in rules["allowedvalues"]:
			return False
		
		# If the value is a string, we can also check for min_length and max_length rules.
		if isinstance(value, str):
			if "min_length" in rules and len(value) < rules["min_length"]:
				return False
			if "max_length" in rules and len(value) > rules["max_length"]:
				return False
		return True

	def _validate_field(self, field_name: str) -> bool:
		"""Helper method to validate a single field based on the VALIDATION_RULES."""
		if field_name not in self.VALIDATION_RULES:
			return True  # No validation rules for this field, consider it valid
		
		# Get the validation rules for the field from the VALIDATION_RULES dict.
		rules = self.VALIDATION_RULES[field_name]
		# Get the value of the field from the instance using getattr.
		# This will raise an exception if the field name does not exist.
		value = getattr(self, field_name)

		if value is None:
			return True  # Optional field not provided, consider it valid
		
		# If the value is a list and the rules allow multiple values,
		# validate each item in the list against the same rules.
		if isinstance(value, list) and rules.get("multi", False):
			return all(self._validate_field_value(v, rules) for v in value)

		return self._validate_field_value(value, rules)
	
	def validate_schema(self) -> bool:
		"""Helper method to validate all fields based on the VALIDATION_RULES."""
		for field_name in self.VALIDATION_RULES.keys():
			if not self._validate_field(field_name):
				return False
		return True
	
class CounterStrikeSpec(GameProfileSpec):
	game_name = "Counter-Strike 2"
	game_slug = "cs2"

	VALIDATION_RULES: ClassVar[dict[str, dict[str, object]]] = {
		"premier_rank": {
			"allowedvalues": [
				"Unranked",
				"0-5k",
				"5k-10k",
				"10k-15k",
				"15k-20k",
				"20k-25k",
				"25k-30k",
				"30k+",
			]
		},
		"role": {
			"allowedvalues": [
				"Entry Fragger", 
				"Support", 
				"AWPer", 
				"In-Game Leader", 
				"Lurker"
			],
			"multi": True  # Allow multiple roles to be selected
		}
	}

	premier_rank: int | None = None
	role: str | None = None
	
class LeagueOfLegendsSpec(GameProfileSpec):
	game_name = "League of Legends"
	game_slug = "league-of-legends"

	VALIDATION_RULES: ClassVar[dict[str, dict[str, object]]] = {
		"rank": {
			"allowedvalues": ["Iron", "Bronze", "Silver", "Gold", "Platinum", "Diamond", "Master", "Grandmaster", "Challenger"]
		},
		"main_role": {
			"allowedvalues": ["Top", "Jungle", "Mid", "ADC", "Support"]
		}
	}

	rank: str | None = None
	main_role: str | None = None
	
class ValorantSpec(GameProfileSpec):
	game_name = "Valorant"
	game_slug = "valorant"

	VALIDATION_RULES: ClassVar[dict[str, dict[str, object]]] = {
		"rank": {
			"allowedvalues": ["Iron", "Bronze", "Silver", "Gold", "Platinum", "Diamond", "Immortal", "Radiant"]
		},
		"main_agent": {
			"max_length": 50
		}
	}

	rank: str | None = None
	main_agent: str | None = None

class ApexLegendsSpec(GameProfileSpec):
	game_name = "Apex Legends"
	game_slug = "apex-legends"

	VALIDATION_RULES: ClassVar[dict[str, dict[str, object]]] = {
		"rank": {
			"allowedvalues": ["Bronze", "Silver", "Gold", "Platinum", "Diamond", "Master", "Apex Predator"]
		},
		"main_legend": {
			"max_length": 50
		}
	}

	rank: str | None = None
	main_legend: str | None = None

class ArcRaidersSpec(GameProfileSpec):
	game_name = "Arc Raiders"
	game_slug = "arc-raiders"

	VALIDATION_RULES: ClassVar[dict[str, dict[str, object]]] = {
		"rank": {
			"allowedvalues": ["Bronze", "Silver", "Gold", "Platinum", "Diamond", "Master", "Grandmaster"]
		},
		"main_hero": {
			"max_length": 50
		}
	}

	rank: str | None = None
	main_hero: str | None = None

class MobileLegendsSpec(GameProfileSpec):
	game_name = "Mobile Legends"
	game_slug = "mobile-legends"

	VALIDATION_RULES: ClassVar[dict[str, dict[str, object]]] = {
		"rank": {
			"allowedvalues": ["Warrior", "Elite", "Master", "Grandmaster", "Epic", "Legend", "Mythic", "Mythical Immortal"]
		},
		"main_hero": {
			"max_length": 50
		}
	}

	rank: str | None = None
	main_hero: str | None = None

class MinecraftSpec(GameProfileSpec):
	game_name = "Minecraft"
	game_slug = "minecraft"

	VALIDATION_RULES: ClassVar[dict[str, dict[str, object]]] = {
		"preferred_mode": {
			"allowedvalues": ["Survival", "Creative", "Adventure", "Spectator"]
		},
		"favorite_mod": {
			"max_length": 100
		}
	}

	preferred_mode: str | None = None
	favorite_mod: str | None = None

class PUBGSpec(GameProfileSpec):
	game_name = "PUBG: Battlegrounds"
	game_slug = "pubg"

	VALIDATION_RULES: ClassVar[dict[str, dict[str, object]]] = {
		"rank": {
			"allowedvalues": ["Bronze", "Silver", "Gold", "Platinum", "Diamond", "Master", "Grandmaster"]
		},
		"main_weapon": {
			"max_length": 50
		}
	}

	rank: str | None = None
	main_weapon: str | None = None

class CallOfDutySpec(GameProfileSpec):
	game_name = "Call of Duty: Warzone"
	game_slug = "call-of-duty-warzone"

	VALIDATION_RULES: ClassVar[dict[str, dict[str, object]]] = {
		"main_weapon": {
			"max_length": 50
		},
		"preferred_mode": {
			"allowedvalues": ["Battle Royale", "Plunder", "Resurgence"]
		}
	}

	main_weapon: str | None = None
	preferred_mode: str | None = None

class RustSpec(GameProfileSpec):
	game_name = "Rust"
	game_slug = "rust"

	VALIDATION_RULES: ClassVar[dict[str, dict[str, object]]] = {
		"playstyle": {
			"allowedvalues": ["Solo", "Duo", "Squad"]
		},
		"main_weapon": {
			"max_length": 50
		}
	}

	playstyle: str | None = None
	main_weapon: str | None = None

class EscapeFromTarkovSpec(GameProfileSpec):
	game_name = "Escape From Tarkov"
	game_slug = "escape-from-tarkov"

	VALIDATION_RULES: ClassVar[dict[str, dict[str, object]]] = {
		"faction": {
			"allowedvalues": ["USEC", "BEAR", "Scav"]
		},
		"main_weapon": {
			"max_length": 50
		},
		"playstyle": {
			"allowedvalues": ["Aggressive", "Stealthy", "Balanced"]
		}
	}

	faction: str | None = None
	main_weapon: str | None = None
	playstyle: str | None = None

class Dota2Spec(GameProfileSpec):
	game_name = "Dota 2"
	game_slug = "dota-2"

	VALIDATION_RULES: ClassVar[dict[str, dict[str, object]]] = {
		"rank": {
			"allowedvalues": ["Herald", "Guardian", "Crusader", "Archon", "Legend", "Ancient", "Divine", "Immortal"]
		},
	}

	rank: str | None = None

class GTAVSpec(GameProfileSpec):
	game_name = "GTA V"
	game_slug = "gta-v"

	VALIDATION_RULES: ClassVar[dict[str, dict[str, object]]] = {
		"preferred_mode": {
			"allowedvalues": ["Story Mode", "Online Freemode", "Online Heists", "Online Races", "Online Other"]
		},
		"main_activity": {
			"max_length": 100
		}
	}

	preferred_mode: str | None = None
	main_activity: str | None = None

class RobloxSpec(GameProfileSpec):
	game_name = "Roblox"
	game_slug = "roblox"

	VALIDATION_RULES: ClassVar[dict[str, dict[str, object]]] = {
		"favorite_game": {
			"max_length": 100
		},
		"preferred_genre": {
			"allowedvalues": ["Adventure", "Roleplay", "Simulator", "Obby", "Tycoon", "FPS", "Horror", "Other"]
		}
	}

	favorite_game: str | None = None
	preferred_genre: str | None = None

class OverwatchSpec(GameProfileSpec):
	game_name = "Overwatch 2"
	game_slug = "overwatch-2"

	VALIDATION_RULES: ClassVar[dict[str, dict[str, object]]] = {
		"rank": {
			"allowedvalues": ["Bronze", "Silver", "Gold", "Platinum", "Diamond", "Master", "Grandmaster", "Top 500"]
		},
		"main_hero": {
			"max_length": 50
		}
	}

	rank: str | None = None
	main_hero: str | None = None

class WorldOfWarcraftSpec(GameProfileSpec):
	game_name = "World of Warcraft"
	game_slug = "world-of-warcraft"

	VALIDATION_RULES: ClassVar[dict[str, dict[str, object]]] = {
		"main_class": {
			"allowedvalues": ["Warrior", "Paladin", "Hunter", "Rogue", "Priest", "Death Knight", "Shaman", "Mage", "Warlock", "Monk", "Druid", "Demon Hunter"]
		},
		"main_role": {
			"allowedvalues": ["Tank", "Healer", "DPS"]
		}
	}

	main_class: str | None = None
	main_role: str | None = None

class MarvelRivalsSpec(GameProfileSpec):
	game_name = "Marvel Rivals"
	game_slug = "marvel-rivals"

	VALIDATION_RULES: ClassVar[dict[str, dict[str, object]]] = {
		#TODO: Add real validation rules for this game profile. I don't know enough about the game to add this.
	}

class FIFASpec(GameProfileSpec):
	game_name = "FIFA"
	game_slug = "fifa"

	VALIDATION_RULES: ClassVar[dict[str, dict[str, object]]] = {
		#TODO: Add real validation rules for this game profile. I don't know enough about the game to add this.
	}

class DiabloSpec(GameProfileSpec):
	game_name = "Diablo IV"
	game_slug = "diablo-iv"

	VALIDATION_RULES: ClassVar[dict[str, dict[str, object]]] = {
		"main_class": {
			"allowedvalues": ["Barbarian", "Druid", "Necromancer", "Rogue", "Sorcerer"]
		},
		"playstyle": {
			"allowedvalues": ["Solo", "Duo", "Squad"]
		}
	}

	main_class: str | None = None
	playstyle: str | None = None

class EldenRingSpec(GameProfileSpec):
	game_name = "Elden Ring"
	game_slug = "elden-ring"

	VALIDATION_RULES: ClassVar[dict[str, dict[str, object]]] = {
		"main_class": {
			"allowedvalues": ["Vagabond", "Warrior", "Hero", "Bandit", "Astrologer", "Prophet", "Samurai", "Prisoner", "Confessor", "Wretch"]
		},
		"playstyle": {
			"allowedvalues": ["Melee", "Ranged", "Magic", "Stealth"]
		}
	}

	main_class: str | None = None
	playstyle: str | None = None

class GenshinImpactSpec(GameProfileSpec):
	game_name = "Genshin Impact"
	game_slug = "genshin-impact"

	VALIDATION_RULES: ClassVar[dict[str, dict[str, object]]] = {
		"main_character": {
			"max_length": 50
		},
		"preferred_role": {
			"allowedvalues": ["DPS", "Support", "Healer", "Sub-DPS"]
		}
	}

	main_character: str | None = None
	preferred_role: str | None = None

class FortniteSpec(GameProfileSpec):
	game_name = "Fortnite"
	game_slug = "fortnite"

	VALIDATION_RULES: ClassVar[dict[str, dict[str, object]]] = {
		"preferred_mode": {
			"allowedvalues": ["Solo", "Duo", "Squad"]
		},
		"main_weapon": {
			"max_length": 50
		}
	}

	preferred_mode: str | None = None
	main_weapon: str | None = None