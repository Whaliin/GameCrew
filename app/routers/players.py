from random import random

from fastapi import APIRouter, HTTPException

router = APIRouter(prefix="/api/players", tags=["players"])

@router.get("/{username}")
def get_player_profile(username: str):
	# return sample data for now
	# TODO: replace with real database query

	profile = {
		"avatar_url": "/static/img/profiles/default.jpg",
		"username": username,
		"user_tag": f"#{username}1234",
		"rank": "Gold Nova III", # TODO: replace with real game rank?
		"age_range": "18-25",
		"platform": "PC",
		"playtime": "Kvällar & Helger",
		"languages": "SV / EN",
		"bio": "This is a sample bio for the player.",
		"games": []
	}

	# Randomly add 1-4 games to the profile for testing
	profile["games"] = [
		{"slug": "cs2", "image_url": "/static/img/games/csgo.jpg", "name": "Counter-Strike 2" }
	]

	if random() < 0.75:
		profile["games"].append({"slug": "lol", "image_url": "/static/img/games/lol.jpg", "name": "League of Legends" })

	if random() < 0.5:
		profile["games"].append({"slug": "valorant", "image_url": "/static/img/games/valorant.jpg", "name": "Valorant" })

	if random() < 0.25:
		profile["games"].append({"slug": "arc", "image_url": "/static/img/games/arcraiders.jpg", "name": "ARC Raiders" })

	return profile


@router.get("/{username}/stats/{game_slug}")
def get_player_game_stats(username: str, game_slug: str):
	raise HTTPException(
		status_code=501,
		detail=f"TODO: fetch game stats for '{username}' in '{game_slug}'",
	)
