from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, declarative_base, sessionmaker

from app.schemas import GameProfileSpec

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
	import app.models as models  # Ensure all models are imported before creating tables
	Base.metadata.create_all(bind=engine)

	# check if the default data is already seeded (e.g. if there are any games in the database), and if not, seed the default data.
	with SessionLocal() as db:
		if db.query(models.Game).first() is None:
			seed_default_data()
		else:
			# create a schema map (slugs -> schema class)
			schema_map = {s.game_slug: s for s in GameProfileSpec.__subclasses__()}
			# get the set of slugs (unique identifiers)
			code_slugs = set(schema_map.keys())

			# get existing games from the database
			existing_games = {row.slug: row for row in db.query(models.Game).all()}
			# get the set (unique values) of slugs from the database (realistically this does nothing)
			db_slugs = set(existing_games.keys())

			# calculate difference between the sets
			to_create = code_slugs - db_slugs
			to_delete = db_slugs - code_slugs

			# create new games
			for slug in to_create:
				schema = schema_map[slug]
				db.add(models.Game(
					slug=slug, 
					name=schema.game_name, 
					schema_spec=schema.__name__
				))

			# remove games in db but not in code
			if to_delete:
				db.query(models.Game).filter(models.Game.slug.in_(to_delete)).delete()

			# commit changes
			db.commit()
		
		# if db.query(models.PlayerProfile).first() is None:
		# 	seed_player_profiles()

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