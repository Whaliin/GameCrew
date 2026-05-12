import datetime
import json
from random import random
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Request, Response, Form
from fastapi.responses import RedirectResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.auth.hashing import hash_password, verify_password
from app.auth.sessions import get_user
from app.auth.validation import validate_birth_year, validate_username
from app.database import get_db
from app.models import Friendship, Game, Language, Platform, Player, PlayerProfile, PlayerGameProfile, Playtime
from app.routers.pages import get_game_image_url
from app.schemas import GameProfileSpec

router = APIRouter(prefix="/api/players", tags=["players"])

def map_age_range(birth_year: int) -> str:
	"""Map birth year to a coarse age range used in templates.
	
	:param birth_year: The birth year to map.
	:return: A string representing the age range category.
	"""
	age = datetime.datetime.now().year - birth_year
	if age < 18:
		return "Under 18" # This case should be prevented by validation
	if age <= 25:
		return "18-25"
	if age <= 35:
		return "26-35"
	if age <= 45:
		return "36-45"
	return "45+"

def create_profile_object(db: Session, username: str) -> dict | None:
	"""
	Create a profile object for a given username, or return None if user not found.
	
	:param db: Database session for querying user and profile data.
	:param username: The username of the player whose profile to create.
	:return: A dictionary containing the player's profile information, or None if the player is not found.
	"""
	# find the player by username
	player = db.query(Player).filter(Player.username == username).first()
	if not player:
		return None
	
	# TODO: Add the avatar stuff
	# Check if the player has an avatar (check file path based on player_id)

	# build the profile object
	profile = {
		"username": player.username,
		"avatar_url": "/static/img/profiles/default.jpg",
		"discord": player.profile.discord if player.profile.discord else "Not set",
		"steam": player.profile.steam_url if player.profile.steam_url else "Not set",
		"age_range": map_age_range(player.profile.birth_year),
		"region": player.profile.region.name if player.profile.region else "Unknown",
		"platforms": " / ".join([platform.name for platform in player.platforms]) if player.platforms else "Not set",
		"playtimes": " / ".join([playtime.name for playtime in player.playtimes]) if player.playtimes else "Not set",
		"languages": " / ".join([language.name for language in player.languages]) if player.languages else "Not set",
		"bio": player.profile.bio or "",
	}

	return profile

# ===============================================
# 					Player Profiles
# ===============================================
@router.get("/{username}")
def get_player_profile(username: str, db: Session = Depends(get_db)):
	"""
	Get a player's profile by username, including their game profiles.

	:param username: The username of the player whose profile to retrieve.
	:raises HTTPException: 404 if the player is not found.
	:return: A JSON object containing the player's profile information and their game profiles.
	"""
	profile = create_profile_object(db, username)
	if not profile:
		raise HTTPException(status_code=404, detail="Player not found")

	# Fetch player's actual game profiles
	player = db.query(Player).filter(Player.username == username).first()
	if not player:
		raise HTTPException(status_code=404, detail="Player not found")
	
	player_game_profiles = db.query(PlayerGameProfile).filter(
		PlayerGameProfile.player_id == player.id
	).all()

	profile["games"] = []
	for pgp in player_game_profiles:
		# For each game profile, get the game info and include any relevant profile data.
		game = db.query(Game).filter(Game.id == pgp.game_id).first()
		if game:
			game_schema = GameProfileSpec.get_schema(game.schema_spec) if game.schema_spec else None
			display_value = None
			game_data = {
				"slug": game.slug,
				"image_url": get_game_image_url(game.slug),
				"name": game.name,
			}
			# Add game-specific profile data if it exists
			if pgp.data:
				try:
					profile_data = json.loads(pgp.data)
					game_data["profile_data"] = profile_data
					if game_schema:
						display_value = game_schema.get_display_value(profile_data)
						game_data["display_value"] = display_value
				except json.JSONDecodeError:
					pass
			if display_value is not None:
				game_data["display_value"] = display_value
			profile["games"].append(game_data)

	return profile

# ===============================================
# 					Player Game Profiles
# ================================================
# TODO

# ===============================================
# 					Friendships
# ===============================================
@router.post("/{username}/friend")
def add_friend(request: Request, username: str, db: Session = Depends(get_db)):
	"""
	Add a user as a friend.

	:param username: The username of the user to add as a friend. This user must exist and not already be your friend.
	:raises HTTPException: 404 if the user is not found, 400 if already friends or if trying to friend yourself.
	:return: 204 No Content on success.
	"""

	sender = get_user(request, db)
	if not sender:
		raise HTTPException(status_code=401, detail="Not authenticated")

	user = db.query(Player).filter(Player.username == username).first()
	if not user:
		raise HTTPException(status_code=404, detail="User not found")
	
	# Check if the user already has this friend
	existing = db.query(Friendship).filter(
		((Friendship.sender_id == sender.id) & (Friendship.receiver_id == user.id)) |
		((Friendship.sender_id == user.id) & (Friendship.receiver_id == sender.id))
	).first()

	if existing:
		if existing.accepted:
			raise HTTPException(status_code=400, detail="Already friends")
		else:
			raise HTTPException(status_code=400, detail="Friend request already pending")
		
	if sender.id == user.id:
		raise HTTPException(status_code=400, detail="Cannot friend yourself")
		
	# Create a new friend request
	friend_request = Friendship(sender_id=sender.id, receiver_id=user.id, accepted=False)
	db.add(friend_request)
	db.commit()

	return Response(status_code=204)

@router.delete("/{username}/friend")
def remove_friend(request: Request, username: str, db: Session = Depends(get_db)):
	"""
	Remove a user from friends.

	:param username: The username of the friend to remove. This user must already be a friend.
	:raises HTTPException: 404 if the user is not found, 400 if the user is not currently a friend.
	:return: 204 No Content on success.
	"""

	sender = get_user(request, db)
	if not sender:
		raise HTTPException(status_code=401, detail="Not authenticated")

	user = db.query(Player).filter(Player.username == username).first()
	if not user:
		raise HTTPException(status_code=404, detail="User not found")
	
	# Check if the user already has this friend
	existing = db.query(Friendship).filter(
		((Friendship.sender_id == sender.id) & (Friendship.receiver_id == user.id)) |
		((Friendship.sender_id == user.id) & (Friendship.receiver_id == sender.id))
	).first()

	# If no existing friendship or friend request, return an error
	if not existing or not existing.accepted:
		raise HTTPException(status_code=400, detail="Not friends")
		
	db.delete(existing)
	db.commit()

	return Response(status_code=204)

@router.patch("/{username}/friend")
def handle_friend_request(request: Request, username: str, accept: bool, db: Session = Depends(get_db)):
	"""
	Handle a friend request by accepting or rejecting it.

	:param accept: True to accept the friend request, False to reject it.
	:param username: The username of the user who you want to accept/reject a friend request from. This user must have sent you a friend request.
	:raises HTTPException: 404 if the user is not found, 400 if there is no pending friend request from this user.
	:return: 204 No Content on success.
	"""

	sender = get_user(request, db)
	if not sender:
		raise HTTPException(status_code=401, detail="Not authenticated")

	user = db.query(Player).filter(Player.username == username).first()
	if not user:
		raise HTTPException(status_code=404, detail="User not found")
	
	# Check if there is a pending friend request from this user
	existing = db.query(Friendship).filter(
		Friendship.sender_id == user.id,
		Friendship.receiver_id == sender.id,
		Friendship.accepted == False
	).first()

	if not existing:
		raise HTTPException(status_code=400, detail="No pending friend request from this user")
	
	if accept:
		existing.accepted = True
	else:
		db.delete(existing) # TODO: Is this intended behavior?
	
	db.commit()

	return Response(status_code=204)