import datetime
import json
from random import random
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Request, Response
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.auth.hashing import hash_password, verify_password
from app.auth.sessions import get_user
from app.auth.validation import validate_birth_year, validate_username
from app.database import get_db
from app.models import Friendship, Game, Language, Platform, Player, PlayerProfile, PlayerGameProfile, Playtime
from app.routers.pages import get_game_image_url

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
			game_data = {
				"slug": game.slug,
				"image_url": get_game_image_url(game.slug),
				"name": game.name,
			}
			# Add game-specific profile data if it exists
			if pgp.data:
				# TODO: is it up to the frontend to know what value to display as the primary value?
				# schema returns DISPLAY_VALUE for the primary value but this is not displayed here. so it assumes the frontend already knows what to display.
				try:
					game_data["profile_data"] = json.loads(pgp.data)
				except json.JSONDecodeError:
					pass
			profile["games"].append(game_data)

	return profile

class PlayerAccountUpdate(BaseModel):
	"""
	Schema for updating player account information. All fields are optional.
	"""
	username: Optional[str] = None
	current_password: Optional[str] = None
	password: Optional[str] = None

@router.patch("/update/account")
def update_player_account(
	account_data: PlayerAccountUpdate,
	request: Request,
	db: Session = Depends(get_db)
):
	"""
	Update the current player's account information.

	:param account_data: The updated account information.
	:param request: The incoming request containing the updated account data in JSON format.
	:raises HTTPException: 401 if not authenticated, 400 if the input data is invalid.
	:return: A JSON object containing the updated account information.
	"""
	user = get_user(request, db)
	if not user:
		raise HTTPException(status_code=401, detail="Not authenticated")

	update_data = account_data.model_dump(exclude_unset=True)

	if update_data.get("username"):
		if not validate_username(update_data["username"]):
			raise HTTPException(status_code=400, detail="Invalid username")

		# Check if the new username is already taken by another user
		existing_user = db.query(Player).filter(Player.username == update_data["username"]).first()
		if existing_user and existing_user.id != user.id:
			raise HTTPException(status_code=400, detail="Username already taken")
		user.username = update_data["username"]

	if update_data.get("password"):
		# check if current_password is correct
		if not verify_password(update_data["current_password"], user.password_hash):
			raise HTTPException(status_code=400, detail="Current password is incorrect")
		
		user.password_hash = hash_password(update_data["password"])

	return Response(status_code=204)

class PlayerProfileUpdate(BaseModel):
	"""
	Schema for updating player profile information. All fields are optional.
	"""
	# image
	bio: Optional[str] = None
	birth_year: Optional[int] = None
	region_id: Optional[int] = None
	languages: Optional[List[str]] = None
	platforms: Optional[List[str]] = None
	playtimes: Optional[List[str]] = None
	steam_url: Optional[str] = None
	discord: Optional[str] = None

@router.patch("/update/profile")
def update_player_profile(
	profile_data: PlayerProfileUpdate,
	request: Request, 
	db: Session = Depends(get_db)):
	"""
	Update the current player's profile information.

	:param request: The incoming request containing the updated profile data in JSON format.
	:raises HTTPException: 401 if not authenticated, 400 if the input data is invalid.
	:return: A JSON object containing the updated profile information.
	"""
	user = get_user(request, db)
	if not user:
		raise HTTPException(status_code=401, detail="Not authenticated")
	
	update_data = profile_data.model_dump(exclude_unset=True)

	try:
		if update_data.get("bio") is not None:
			user.profile.bio = update_data["bio"]

		if update_data.get("birth_year") is not None:
			birth_year_error = validate_birth_year(update_data["birth_year"])
			if birth_year_error:
				raise HTTPException(status_code=400, detail=birth_year_error)
			user.profile.birth_year = update_data["birth_year"]

		if update_data.get("region_id") is not None:
			user.profile.region_id = update_data["region_id"]

		if update_data.get("languages") is not None:
			user.languages = []
			for language_name in update_data["languages"]:
				language = db.query(Language).filter(Language.name == language_name).first()
				if language:
					user.languages.append(language)
		
		if update_data.get("platforms") is not None:
			user.platforms = []
			for platform_name in update_data["platforms"]:
				platform = db.query(Platform).filter(Platform.name == platform_name).first()
				if platform:
					user.platforms.append(platform)

		if update_data.get("playtimes") is not None:
			user.playtimes = []
			for playtime_name in update_data["playtimes"]:
				playtime = db.query(Playtime).filter(Playtime.name == playtime_name).first()
				if playtime:
					user.playtimes.append(playtime)

		if update_data.get("steam_url") is not None:
			# TODO: steam url validation
			user.profile.steam_url = update_data["steam_url"]

		if update_data.get("discord") is not None:
			user.profile.discord = update_data["discord"]
		
		db.commit()
	except Exception as e:
		db.rollback()
		raise e

	return Response(status_code=204)

@router.patch("/update/privacy")
def update_player_privacy(
	private: bool,
	request: Request, 
	db: Session = Depends(get_db)
):
	"""
	Update the current player's profile privacy setting.

	:param private: A boolean indicating whether the profile should be private (true) or public (false).
	:param request: The incoming request containing the updated privacy setting.
	:raises HTTPException: 401 if not authenticated.
	:return: A JSON object containing the updated privacy setting.
	"""
	user = get_user(request, db)
	if not user:
		raise HTTPException(status_code=401, detail="Not authenticated")
	
	user.profile.private = private
	db.commit()

	return Response(status_code=204)
	

# ===============================================
# 					Player Game Profiles
# ================================================

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