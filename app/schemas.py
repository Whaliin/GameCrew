from pydantic import BaseModel


class PlayerProfile(BaseModel):
	username: str
	avatar_url: str | None = None
	bio: str | None = None
	favorite_games: list[str] = []
	discord_handle: str | None = None
	steam_profile_url: str | None = None


class Game(BaseModel):
	slug: str
	display_name: str
