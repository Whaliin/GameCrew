"""
Utility functions for handling assets (avatars and game images)
"""

from pathlib import Path

def get_avatar_url(player_id: int) -> str:
	"""Get the avatar URL for a given player ID. If no custom avatar exists, returns the default avatar URL."""
	avatar_path = f"static/img/profiles/{player_id}.jpg"

	if Path(avatar_path).exists():
		return "/" + avatar_path
	
	return "/static/img/profiles/default.jpg"

IMG_EXTENSIONS = ("jpg", "png", "webp", "jpeg")
STATIC_GAMES_DIR = Path("static/img/games/")

def get_game_image_url(game_slug: str) -> str:
	"""Get the image URL for a given game slug."""
	# check if the slug exists in file path
	for ext in IMG_EXTENSIONS:
		image_path = STATIC_GAMES_DIR / f"{game_slug}.{ext}"
		if image_path.exists():
			return "/" + str(image_path)
		
	# If not found, return a default image URL
	return "/static/img/games/default.jpg"