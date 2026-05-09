from collections.abc import Generator

from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session, declarative_base, sessionmaker

DATABASE_URL = "sqlite:///./gamecrew.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db() -> Generator[Session, None, None]:
	"""Yield a database session for dependency injection."""
	db = SessionLocal()
	try:
		yield db
	finally:
		db.close()

def init_database() -> None:
	"""Initialize database tables."""
	import app.models  # Ensure all models are imported before creating tables
	Base.metadata.create_all(bind=engine)

DEFAULT_LANGUAGES = [
	{"name": "English"},
	{"name": "Swedish", "localized_name": "Svenska"},
	{"name": "German", "localized_name": "Deutsch"},
	{"name": "Spanish", "localized_name": "Español"},
	{"name": "Arabic", "localized_name": "العربية"},
	{"name": "Mandarin", "localized_name": "简体中文"},
	{"name": "Japanese", "localized_name": "日本語"},
	{"name": "Korean", "localized_name": "한국어"},
	{"name": "French", "localized_name": "Français"},
	{"name": "Russian", "localized_name": "Русский"},
	{"name": "Portuguese", "localized_name": "Português"},
	{"name": "Ukrainian", "localized_name": "Українська"},
	{"name": "Turkish", "localized_name": "Türkçe"},
	{"name": "Italian", "localized_name": "Italiano"},
	{"name": "Polish", "localized_name": "Polski"},
	{"name": "Hindi", "localized_name": "हिन्दी"}
]

DEFAULT_PLATFORMS = [
	"PC", "PlayStation", "Xbox", "Switch", "Mobile"
]

DEFAULT_REGIONS = [
	# North america
	"NA West", "NA Central", "NA East", 
	# Central and south america
	"Central America", "South America", 
	# Europe
	"EU North", "EU Central", "EU South", "EU East", "EU West",
	# ME/Africa
	"Middle East", "North Africa", "Sub-Saharan Africa",
	# Asia
	"Asia West", "Asia North", "Asia South", "Asia East",
	# Oceania
	"Oceania"
]

DEFAULT_PLAYTIMES = [
	"Morning",
	"Afternoon",
	"Evening",
	"Night",
	"Weekends only"
]

def seed_default_data() -> None:
	"""Insert default lookup and game rows if they do not exist yet."""
	# Import the models
	from app.models import Game, Language, Platform, Region, Playtime

	# Get a database session
	db = SessionLocal()
	try:
		# Get the list of existing games to avoid duplicates, then add any missing ones
		existing_slugs = {row.slug for row in db.query(Game).all()}

		# Get the list of defined schemas from the GameProfileSpec subclasses, and insert any missing games
		from app.schemas import GameProfileSpec
		defined_schemas = GameProfileSpec.__subclasses__()
		for schema in defined_schemas:
			# if the slug does not exist, insert a new game row with the corresponding name, slug and schema typename.
			if schema.game_slug not in existing_slugs:
				new_game = Game(
					slug=schema.game_slug, 
					name=schema.game_name, 
					schema_spec=schema.__name__
				)
				db.add(new_game)

		# Seed the default languages, platforms, playtimes, and regions if they do not exist yet
		existing_languages = {row.name for row in db.query(Language).all()}
		for language in DEFAULT_LANGUAGES:
			if language["name"] not in existing_languages:
				db.add(Language(name=language["name"], localized_name=language.get("localized_name")))

		existing_platforms = {row.name for row in db.query(Platform).all()}
		for platform in DEFAULT_PLATFORMS:
			if platform not in existing_platforms:
				db.add(Platform(name=platform))

		existing_regions = {row.name for row in db.query(Region).all()}
		for region in DEFAULT_REGIONS:	
			if region not in existing_regions:
				db.add(Region(name=region))

		existing_playtimes = {row.name for row in db.query(Playtime).all()}
		for playtime in DEFAULT_PLAYTIMES:
			if playtime not in existing_playtimes:
				db.add(Playtime(name=playtime))

		# Finally, commit the changes to the database.
		db.commit()
	except Exception:
		# If any error occurs, rollback the transaction.
		db.rollback()
		raise
	finally:
		# Always close the connection.
		db.close()

def _pick_sample_size(max_size: int) -> int:
	"""Helper function to pick a random sample size between 1 and max_size.
	This function is heavily weighted towards smaller sample sizes to create varied but realistic data 
	(most people play on 1-2 platforms, speak 1-2 languages, and have 1-2 playtimes).
	"""
	from random import choices
	# The buckets represent the possible sample sizes (1,2,3,4,5)
	buckets = [1, 2, 3, 4, 5]
	# 1: chance of picking the first bucket, 2: chance of picking the second bucket, etc,
	weights = [50, 30, 10, 5, 5]
	size = choices(buckets, weights=weights, k=1)[0]
	return min(size, max_size)

def _pick_random_time(days_back: int = 30):
	"""Helper function to pick a random datetime within the last days_back days (default 30)."""
	from datetime import datetime, timedelta
	from random import randint
	return datetime.now() - timedelta(days=randint(0, days_back), minutes=randint(0, 1440))

def seed_player_profiles() -> None:
	"""Seed player profiles with dummy data for testing purposes."""
	from app.models import Player, PlayerProfile, Region, Platform, Language, Playtime, Game, PlayerGameProfile, Friendship
	from app.schemas import GameProfileSpec
	from random import choice, randint, sample

	db = SessionLocal()
	try:
		# Check if there are any existing player profiles to avoid duplicates
		if db.query(PlayerProfile).first() is not None:
			return
		
		# Get the existing values available for selection in the player profiles so we can assign valid values
		regions = db.query(Region).all()
		if not regions:
			raise Exception("No regions found in the database. Please seed the default regions first.")
		
		platforms = db.query(Platform).all()
		if not platforms:
			raise Exception("No platforms found in the database. Please seed the default platforms first.")
		
		languages = db.query(Language).all()
		if not languages:
			raise Exception("No languages found in the database. Please seed the default languages first.")

		playtimes = db.query(Playtime).all()
		if not playtimes:
			raise Exception("No playtimes found in the database. Please seed the default playtimes first.")
		
		games = db.query(Game).all()
		if not games:
			raise Exception("No games found in the database. Please seed the default games first.")
		
		# Add 1000 dummy player profiles with random valid data for testing purposes.
		for i in range(1000):
			player = Player(
				username=f"player{i}",
				password_hash="hashedpassword"
			)
			db.add(player)
			db.flush()  # Flush to get the player ID for the profile (updates the object)

			profile = PlayerProfile(
				player_id=player.id,
				region_id=choice(regions).id,
				birth_year=randint(1950, 2005),
				private=choice([True, False]),
				bio=f"This is the bio of player{i}. I am a gamer who loves playing games and making friends. Looking for people to play with!",
				steam_url=choice([f"https://steamcommunity.com/id/player{i}", None]),
				discord=choice([f"player{i}#1234", None]),
				last_update=_pick_random_time(60)
			)
			db.add(profile)

			# Add random selections of platforms, languages, playtimes for each player profile.
			# Distribution is weighted towards smaller sample size to create more realistic data.
			platforms_sample = sample(platforms, k=_pick_sample_size(len(platforms)))
			player.platforms.extend(platforms_sample)

			languages_sample = sample(languages, k=_pick_sample_size(len(languages)))
			player.languages.extend(languages_sample)

			playtimes_sample = sample(playtimes, k=_pick_sample_size(len(playtimes)))
			player.playtimes.extend(playtimes_sample)

			# For the game profiles, we can add some JSON data based on the game's schema_spec.
			# Pick a random assortment of games for each player profile to create varied test data.
			games_sample = sample(games, k=randint(1, len(games)))
			for game in games_sample:
				# Get the schema class for the game based on the schema_spec field
				# and generate some random valid data based on the field types and validation rules defined in the schema.
				schema_class = GameProfileSpec.get_schema(game.schema_spec)
				if schema_class is None:
					continue  # Skip if no valid schema class is found

				# 20% of profiles will have empty game profile data (to test how the system handles missing/empty data)
				# For the rest, generate random valid data based on the validation rules defined in the schema.
				if choice([False, False, False, False, True]):  # 20% chance of being True
					continue  # Skip adding game profile data for this player and game, leaving it empty.

				profile_data = {}
				for field_name, rules in schema_class.VALIDATION_RULES.items():
					allowed_values = rules.get("allowedvalues", None)
					if allowed_values:
						# If there are allowed values, pick a random one (or multiple if multi is True)
						if rules.get("multi", False):
							profile_data[field_name] = sample(allowed_values, k=_pick_sample_size(len(allowed_values)))
						else:
							profile_data[field_name] = choice(allowed_values)
					else:
						# If there are no allowed values, generate a random value based on the type of validation rules (e.g min/max for numbers, min_length/max_length for strings)
						if "min" in rules and "max" in rules:
							profile_data[field_name] = randint(rules["min"], rules["max"])
						elif "min_length" in rules and "max_length" in rules:
							length = randint(rules["min_length"], rules["max_length"])
							profile_data[field_name] = f"{field_name}_{i}"[:length]  # Generate a string value based on the field name and player index, truncated to the max length
						else:
							profile_data[field_name] = f"{field_name}_{i}"  # Just generate a string value based on the field name and player index
					
				# Add the game profile data as a JSON string in the PlayerGameProfile table
				db.add(PlayerGameProfile(player_id=player.id, game_id=game.id, data=str(profile_data)))

		# After adding all the player profiles and related data,
		# add some random friendships between players.
		player_ids = [player.id for player in db.query(Player).all()]
		for i in range(2000):  # Add 2000 random friendships
			sender_id, receiver_id = choice(player_ids), choice(player_ids)

			if sender_id == receiver_id:  
				continue # Prevent self-friendship (already enforced by the database constraint, but we can avoid the error by checking here)

			if db.query(Friendship).filter(
				((Friendship.sender_id == sender_id) & (Friendship.receiver_id == receiver_id)) | 
				((Friendship.sender_id == receiver_id) & (Friendship.receiver_id == sender_id))
			).first():
				continue # Skip if a friendship already exists between these two players (in either direction)

			# Add the friendship with a random accepted status (70% accepted, 30% pending) to create varied test data.
			accept_state = choice([True, True, True, False])  # 70% chance of being True
			db.add(Friendship(sender_id=sender_id, receiver_id=receiver_id, accepted=accept_state, accepted_at=_pick_random_time() if accept_state else None))

		# Commit all the changes to the database after seeding.
		db.commit()
	except Exception:
		# On exception, rollback the transaction
		db.rollback()
		raise
	finally:
		# Always close the database connection
		db.close()