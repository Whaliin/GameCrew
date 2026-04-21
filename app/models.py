from sqlalchemy import Column, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Player(Base):
	__tablename__ = "players"

	id: Mapped[int] = mapped_column(primary_key=True, index=True)
	username: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
	birth_year: Mapped[int] = mapped_column(Integer, nullable=False)
	avatar_url: Mapped[str] = mapped_column(String(255), nullable=True)
	bio: Mapped[str] = mapped_column(Text, nullable=True)
	password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
	game_profiles: Mapped[list["PlayerGameProfile"]] = relationship(back_populates="player")


class Game(Base):
	__tablename__ = "games"

	id: Mapped[int] = mapped_column(primary_key=True, index=True)
	slug: Mapped[str] = mapped_column(String(80), unique=True, index=True, nullable=False)
	display_name: Mapped[str] = mapped_column(String(120), nullable=False)

	player_profiles: Mapped[list["PlayerGameProfile"]] = relationship(back_populates="game")


class PlayerGameProfile(Base):
	__tablename__ = "player_game_profiles"

	id: Mapped[int] = mapped_column(primary_key=True, index=True)
	player_id: Mapped[int] = mapped_column(Integer, ForeignKey("players.id"), nullable=False)
	game_id: Mapped[int] = mapped_column(Integer, ForeignKey("games.id"), nullable=False)
	rank_label: Mapped[str] = mapped_column(String(100), nullable=True)

	player: Mapped["Player"] = relationship("Player", back_populates="game_profiles")
	game: Mapped["Game"] = relationship("Game", back_populates="player_profiles")
