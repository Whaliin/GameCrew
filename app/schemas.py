from pydantic import BaseModel

# Pydantic schemas define the shape of API request/response payloads.

#class PlayerProfile(BaseModel):
# 	# Public player profile payload returned by profile-related endpoints.
# 	username: str
# 	avatar_url: str | None = None
# 	bio: str | None = None
# 	favorite_games: list[str] = []
# 	discord_handle: str | None = None
# 	steam_profile_url: str | None = None


#class Game(BaseModel):
#	# Lightweight game payload used in list/detail responses.
#	slug: str
#	name: str
