from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

# SQLAlchemy ORM models map Python classes to DB tables used by the app.

# Player account row with profile metadata and authentication fields.
class Player(Base):
	__tablename__ = "players"

	id: Mapped[int] = mapped_column(primary_key=True, index=True)
	username: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
	private: Mapped[bool] = mapped_column(default=False) # If True, users need to send a friend request first. Not currently implemented
	# TODO: email is unused for now, but we may want to add it back in the future for password recovery
	# email: Mapped[str] = mapped_column(String(120), unique=True, index=True, nullable=False)
	registered_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.now())
	birth_year: Mapped[int] = mapped_column(Integer, nullable=False)
	discord_id: Mapped[str] = mapped_column(String(50), nullable=True)
	steam_id: Mapped[str] = mapped_column(String(50), nullable=True)
	region_id: Mapped[int] = mapped_column(ForeignKey("valid_regions.id"), nullable=False)
	avatar_url: Mapped[str] = mapped_column(String(255), nullable=True)
	bio: Mapped[str] = mapped_column(Text, nullable=True)
	password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
#	game_profiles: Mapped[list["PlayerGameProfile"]] = relationship(back_populates="player")

	region: Mapped["ValidRegions"] = relationship("ValidRegions")
	favorite_games: Mapped[list["PlayerGameFavorites"]] = relationship("PlayerGameFavorites", back_populates="player")

# Friend relationships (many-to-many self-referential)
# We use a single table to track friend requests and their status.
class FriendRequest(Base):
	__tablename__ = "friend_requests"

	id: Mapped[int] = mapped_column(primary_key=True, index=True)
	from_player_id: Mapped[int] = mapped_column(Integer, ForeignKey("players.id"), nullable=False)
	to_player_id: Mapped[int] = mapped_column(Integer, ForeignKey("players.id"), nullable=False)
	accepted: Mapped[bool] = mapped_column(default=False, nullable=True) # None = pending, True = accepted, False = rejected
	sent_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
	accepted_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)

	from_player: Mapped["Player"] = relationship("Player", foreign_keys=[from_player_id])
	to_player: Mapped["Player"] = relationship("Player", foreign_keys=[to_player_id])

class Game(Base):
	__tablename__ = "games"

	id: Mapped[int] = mapped_column(primary_key=True, index=True)
	slug: Mapped[str] = mapped_column(String(80), unique=True, index=True, nullable=False)
	name: Mapped[str] = mapped_column(String(120), nullable=False)

	# Back-reference to association rows linking players that favorited this game.
	players_who_favorited: Mapped[list["PlayerGameFavorites"]] = relationship("PlayerGameFavorites", back_populates="game")

class PlayerGameFavorites(Base):
	__tablename__ = "player_game_favorites"

	player_id: Mapped[int] = mapped_column(Integer, ForeignKey("players.id"), nullable=False, primary_key=True)
	game_id: Mapped[int] = mapped_column(Integer, ForeignKey("games.id"), nullable=False, primary_key=True)

	# Association row between one player and one game.
	player: Mapped["Player"] = relationship("Player", back_populates="favorite_games")
	game: Mapped["Game"] = relationship("Game", back_populates="players_who_favorited")

class ValidRegions(Base):
	__tablename__ = "valid_regions"

	id: Mapped[int] = mapped_column(primary_key=True, index=True)
	# Region labels used by player profiles.
	name: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)

# Contains valid playtime preferences that players can select from
# Example: "Morgon", "Dag", "Kväll", "Natt"
class PlaytimePreferences(Base):
	__tablename__ = "playtime_preferences"

	id: Mapped[int] = mapped_column(primary_key=True, index=True)
	name: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)

# Association table linking players to their selected playtime preferences
class PlayerPlaytimePreferences(Base):
	__tablename__ = "player_playtime_preferences"

	player_id: Mapped[int] = mapped_column(Integer, ForeignKey("players.id"), nullable=False, primary_key=True)
	playtime_preference_id: Mapped[int] = mapped_column(Integer, ForeignKey("playtime_preferences.id"), nullable=False, primary_key=True)

	player: Mapped["Player"] = relationship("Player")
	playtime_preference: Mapped["PlaytimePreferences"] = relationship("PlaytimePreferences")

# Contains valid platform preferences that players can select from
# Example: "PC", "PlayStation", "Xbox", "Switch", "Mobile"
class PlatformSelections(Base):
	__tablename__ = "platform_selections"

	id: Mapped[int] = mapped_column(primary_key=True, index=True)
	name: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)

# Association table linking players to their selected platform preferences
class PlayerPlatformSelections(Base):
	__tablename__ = "player_platform_selections"

	player_id: Mapped[int] = mapped_column(Integer, ForeignKey("players.id"), nullable=False, primary_key=True)
	platform_selection_id: Mapped[int] = mapped_column(Integer, ForeignKey("platform_selections.id"), nullable=False, primary_key=True)

	player: Mapped["Player"] = relationship("Player")
	platform_selection: Mapped["PlatformSelections"] = relationship("PlatformSelections")

# Contains valid language preferences that players can select from
# Example: "Svenska", "English", "Español", "Deutsch"
class LanguagePreferences(Base):
	__tablename__ = "language_preferences"

	id: Mapped[int] = mapped_column(primary_key=True, index=True)
	name: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)

# Association table linking players to their selected language preferences
class PlayerLanguagePreferences(Base):
	__tablename__ = "player_language_preferences"

	player_id: Mapped[int] = mapped_column(Integer, ForeignKey("players.id"), nullable=False, primary_key=True)
	language_preference_id: Mapped[int] = mapped_column(Integer, ForeignKey("language_preferences.id"), nullable=False, primary_key=True)

	player: Mapped["Player"] = relationship("Player")
	language_preference: Mapped["LanguagePreferences"] = relationship("LanguagePreferences")