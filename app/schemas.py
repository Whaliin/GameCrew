from pydantic import BaseModel

# Pydantic schemas for database game profile models.
# The base class for all schemas is GameProfileSpec, which can be extended with additional fields.
class GameProfileSpec(BaseModel):
	# Default fields that all game profile schemas should have.
	game_name: str
	game_slug: str

	VALIDATION_RULES = {}

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
					"type": cls.__annotations__.get(field_name, "unknown"),
					# Get any validation rules for the field from the VALIDATION_RULES dict.
					"validation": cls.VALIDATION_RULES.get(field_name, {})
					#"optional": True
				}
				for field_name in cls.__annotations__.keys()
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

	VALIDATION_RULES = {
		"premier_rank": {
			"min": 1,
			"max": 30000
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

	VALIDATION_RULES = {
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

	VALIDATION_RULES = {
		"rank": {
			"allowedvalues": ["Iron", "Bronze", "Silver", "Gold", "Platinum", "Diamond", "Immortal", "Radiant"]
		},
		"main_agent": {
			"max_length": 50
		}
	}

	rank: str | None = None
	main_agent: str | None = None