# ============================================================================= 
# Database models for the app. These classes represent the tables in the DB and are used by SQLAlchemy.
# =============================================================================

from datetime import datetime

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Index, Integer, String, Text, Table, Column
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

player_platforms = Table(
    "player_platforms", Base.metadata,
    Column("player_id", Integer, ForeignKey("players.id"), primary_key=True),
    Column("platform_id", Integer, ForeignKey("platforms.id"), primary_key=True),
)

player_languages = Table(
    "player_languages", Base.metadata,
    Column("player_id", Integer, ForeignKey("players.id"), primary_key=True),
    Column("language_id", Integer, ForeignKey("languages.id"), primary_key=True),
)

player_playtimes = Table(
    "player_playtimes", Base.metadata,
    Column("player_id", Integer, ForeignKey("players.id"), primary_key=True),
    Column("playtime_id", Integer, ForeignKey("playtimes.id"), primary_key=True),
)

class Game(Base):
	__tablename__ = "games"

	id: Mapped[int] = mapped_column(primary_key=True, index=True)
	# Name of the game (e.g "Apex Legends", "Fortnite", "Minecraft").
	name: Mapped[str] = mapped_column(String(255), nullable=False)
	# Game slug used for URLs and internal references (e.g "apex-legends", "fortnite", "minecraft").
	slug: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
	# The typename of the corresponding GameProfileSpec subclass (e.g "CounterStrikeSpec", "LeagueOfLegendsSpec", etc).
	# This way we can easily determine for each game which fields the player profiles should have, and how to validate them.
	schema_spec: Mapped[str] = mapped_column(Text, nullable=True)

class Language(Base):
	__tablename__ = "languages"

	id: Mapped[int] = mapped_column(primary_key=True)
	# English name for the language
	name: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
	# The localized name of the language (e.g "Svenska" for Swedish).
	localized_name: Mapped[str] = mapped_column(String(255), nullable=True)

	players: Mapped[list["Player"]] = relationship(
		"Player",
		secondary="player_languages",
		back_populates="languages"
	)

class Platform(Base):
	__tablename__ = "platforms"

	id: Mapped[int] = mapped_column(primary_key=True)
	# Name of the platform (e.g "PC", "PlayStation", "Xbox", "Switch", "Mobile").
	name: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)

	players: Mapped[list["Player"]] = relationship(
		"Player",
		secondary="player_platforms",
		back_populates="platforms"
	)


class Playtime(Base):
	__tablename__ = "playtimes"

	id: Mapped[int] = mapped_column(primary_key=True)
	# Name of the playtime (e.g "Morning", "Afternoon", "Evening", "Night", "Weekends only").
	name: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)

	players: Mapped[list["Player"]] = relationship(
		"Player",
		secondary="player_playtimes",
		back_populates="playtimes"
	)

class Region(Base):
	__tablename__ = "regions"

	id: Mapped[int] = mapped_column(primary_key=True)
	# Name of the region (e.g "NA West", "EU Central", "Asia East").
	name: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)

# Player related tables
class Player(Base):
	__tablename__ = "players"

	id: Mapped[int] = mapped_column(primary_key=True)
	created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.now())
	username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
	password_hash: Mapped[str] = mapped_column(String(255), nullable=False)

	profile: Mapped["PlayerProfile"] = relationship("PlayerProfile", uselist=False, back_populates="player")
	platforms: Mapped[list["Platform"]] = relationship(
		"Platform",
		secondary="player_platforms",
		back_populates="players"
	)
	playtimes: Mapped[list["Playtime"]] = relationship(
		"Playtime",
		secondary="player_playtimes",
		back_populates="players"
	)
	languages: Mapped[list["Language"]] = relationship(
		"Language",
		secondary="player_languages",
		back_populates="players"
	)

# Player profile data
class PlayerProfile(Base):
	__tablename__ = "player_profiles"
	player_id: Mapped[int] = mapped_column(Integer, ForeignKey("players.id"), primary_key=True)
	region_id: Mapped[int] = mapped_column(Integer, ForeignKey("regions.id"), nullable=False)
	# Year of birth (e.g 2001, 1995). We don't want to store full birthdates for privacy reasons
	birth_year: Mapped[int] = mapped_column(Integer)
	# Whether the player wants their profile information to be private or public.
	# If private, the external links will not be displayed until the users become friends.
	private: Mapped[bool] = mapped_column(default=False)
	# The last time the player's profile was updated.
	last_update: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.now())
	# A bio or description that the player can write about themselves.
	bio: Mapped[str] = mapped_column(String(500), nullable=True)
	# TODO: how do we store this? full steampowered url, or just the username/id?
	steam_url: Mapped[str] = mapped_column(String(255), nullable=True)
	# TODO: is there a way we can validate discord usernames?
	discord: Mapped[str] = mapped_column(String(255), nullable=True)

	player: Mapped["Player"] = relationship("Player", back_populates="profile")
	region: Mapped["Region"] = relationship("Region")

# Player game profile data (e.g rank, playtime, etc)
class PlayerGameProfile(Base):
	__tablename__ = "player_games"

	player_id: Mapped[int] = mapped_column(Integer, ForeignKey("players.id"), primary_key=True)
	game_id: Mapped[int] = mapped_column(Integer, ForeignKey("games.id"), primary_key=True)

	# The actual profile data will be stored as a JSON string, since different games can have different fields.
	# The schema_spec field in the Game table will tell us how to validate and interpret this JSON data for each game.
	data: Mapped[str] = mapped_column(Text, nullable=True)

	player: Mapped["Player"] = relationship("Player")
	game: Mapped["Game"] = relationship("Game")

# Friendship table to represent friend relationships between players.
class Friendship(Base):
	__tablename__ = "friendships"
	__table_args__ = (
		# Add a constraint to prevent a player from being friends with themselves.
		# In future implementations, its a good idea to prevent duplicate friendships as well
		# For example, if a player A sends a friend request to player B, we should prevent player B from sending a friend request back to player A until the first request is accepted or rejected.
		CheckConstraint("sender_id != receiver_id", name="no_self_friendship"),
		Index("idx_sender_receiver", "sender_id", "receiver_id"),
		Index("idx_receiver_sender", "receiver_id", "sender_id")
	)

	sender_id: Mapped[int] = mapped_column(Integer, ForeignKey("players.id"), primary_key=True)
	receiver_id: Mapped[int] = mapped_column(Integer, ForeignKey("players.id"), primary_key=True)
	accepted: Mapped[bool] = mapped_column(default=False, nullable=False)
	sent_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.now())
	accepted_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)

	sender: Mapped["Player"] = relationship("Player", foreign_keys=[sender_id])
	receiver: Mapped["Player"] = relationship("Player", foreign_keys=[receiver_id])