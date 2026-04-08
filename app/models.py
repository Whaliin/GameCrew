from sqlalchemy import Column, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.database import Base


class Player(Base):
    __tablename__ = "players"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    avatar_url = Column(String(255), nullable=True)
    bio = Column(Text, nullable=True)

    game_profiles = relationship("PlayerGameProfile", back_populates="player")


class Game(Base):
    __tablename__ = "games"

    id = Column(Integer, primary_key=True, index=True)
    slug = Column(String(80), unique=True, index=True, nullable=False)
    display_name = Column(String(120), nullable=False)

    player_profiles = relationship("PlayerGameProfile", back_populates="game")


class PlayerGameProfile(Base):
    __tablename__ = "player_game_profiles"

    id = Column(Integer, primary_key=True, index=True)
    player_id = Column(Integer, ForeignKey("players.id"), nullable=False)
    game_id = Column(Integer, ForeignKey("games.id"), nullable=False)
    rank_label = Column(String(100), nullable=True)

    player = relationship("Player", back_populates="game_profiles")
    game = relationship("Game", back_populates="player_profiles")


def get_model_registry_stub() -> list[str]:
    """Return model names to simplify future migration tooling."""
    return ["Player", "Game", "PlayerGameProfile"]
