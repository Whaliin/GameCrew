from pydantic import BaseModel


class PlayerProfileStub(BaseModel):
    username: str
    avatar_url: str | None = None
    bio: str | None = None
    favorite_games: list[str] = []
    discord_handle: str | None = None
    steam_profile_url: str | None = None


class GameStub(BaseModel):
    slug: str
    display_name: str


def get_schema_version_stub() -> str:
    """Return a placeholder schema version string."""
    return "v0-stub"
