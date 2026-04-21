from collections.abc import Generator

from sqlalchemy import create_engine
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
	Base.metadata.create_all(bind=engine)
	seed_default_data()


def _seed_named_rows(db: Session, model, names: list[str]) -> None:
	"""Insert missing rows for lookup tables with a `name` column."""
	# get existing names to avoid duplicates, then add any missing ones
	existing_names = {row.name for row in db.query(model).all()}
	rows_to_add = [model(name=name) for name in names if name not in existing_names]
	if rows_to_add:
		db.add_all(rows_to_add)


def seed_default_data() -> None:
	"""Insert default lookup and game rows if they do not exist yet."""
	from app.models import Game, LanguagePreferences, PlatformSelections, PlaytimePreferences, ValidRegions

	db = SessionLocal()
	try:
		_seed_named_rows(db, ValidRegions, [
			"NA West", "NA Central", "NA East", 
			"Central America", "South America", 
			"EU North", "EU Central", "EU South", "EU East", "EU West",
			"Middle East", "North Africa", "Sub-Saharan Africa",
			"Asia West", "Asia North", "Asia South", "Asia East",
			"Oceania"
		])
		_seed_named_rows(db, PlaytimePreferences, [
			"Morning", "Day", "Evening", "Night"
		])
		_seed_named_rows(db, PlatformSelections, [
			"PC", "PlayStation", "Xbox", "Switch", "Mobile"
		])
		_seed_named_rows(db, LanguagePreferences, [
			"Other", "Swedish (Svenska)", "English", 
			"German (Deutsch)", "Spanish (Español)", "Arabic (العربية)",
			"Mandarin (简体中文)", "Japanese (日本語)", "Korean (한국어)",
			"French (Français)", "Russian (Русский)", "Portuguese (Português)",
			"Ukrainian (Українська)", "Turkish (Türkçe)", "Italian (Italiano)",
			"Polish (Polski)", "Hindi (हिन्दी)"
		])

		default_games = [
			("cs2", "Counter-Strike 2"),
			("lol", "League of Legends"),
			("valorant", "Valorant"),
			("arcraiders", "ARC Raiders"),
			("mobilelegends", "Mobile Legends"),
			("apex", "Apex Legends"),
			("minecraft", "Minecraft"),
		]
		existing_slugs = {row.slug for row in db.query(Game).all()}
		games_to_add = [
			Game(slug=slug, display_name=display_name)
			for slug, display_name in default_games
			if slug not in existing_slugs
		]
		if games_to_add:
			db.add_all(games_to_add)

		db.commit()
	except Exception:
		db.rollback()
		raise
	finally:
		db.close()
