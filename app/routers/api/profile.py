
from typing import List

from fastapi import APIRouter, Depends, Form, HTTPException, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from app.auth.hashing import hash_password, verify_password
from app.auth.sessions import get_session, get_session_id, get_user
from app.auth.validation import validate_birth_year, validate_username
from app.database import get_db
from app.models import Language, Platform, Player, Playtime, Region


router = APIRouter(prefix="/api/profile", tags=["profile"])

@router.post("/settings/account")
def update_player_account(
	request: Request,
	db: Session = Depends(get_db),
	username: str = Form(...),
	current_password: str = Form(None),
	new_password: str = Form(None),
	confirm_password: str = Form(None)
):
	"""
	Update the current player's account settings, including username and password.

	:param request: The incoming request containing the updated account settings in form data.
	:param username: The new username for the player. Must be unique and valid if provided.
	:param current_password: The player's current password, required if changing password.
	:param new_password: The new password for the player. Must match confirm_password if provided.
	:param confirm_password: Confirmation of the new password. Must match new_password if provided.
	:raises HTTPException: 401 if not authenticated, 400 if the input data is invalid (e.g. username taken, passwords don't match, current password incorrect).
	:return: A redirect response to the account settings page on success.
	"""
	user = get_user(request, db)
	if not user:
		raise HTTPException(status_code=401, detail="Not authenticated")
	
	if username and username != user.username:
		username_error = validate_username(username)
		if username_error:
			raise HTTPException(status_code=400, detail="Invalid username: " + username_error)
		
		existing_user = db.query(Player).filter(Player.username == username).first()
		if existing_user:
			raise HTTPException(status_code=400, detail="Username already taken")
		user.username = username

	# Handle Password Change
	if new_password:
		# validate new password and confirmation
		if new_password != confirm_password:
			raise HTTPException(status_code=400, detail="Passwords do not match")
		
		# verify the current password before allowing the change
		if not current_password or not verify_password(current_password, user.password_hash):
			raise HTTPException(status_code=400, detail="Current password required/incorrect")
		
		user.password_hash = hash_password(new_password)

	db.commit()

	# update the session username
	session_id = get_session_id(request)
	if session_id:
		session = get_session(session_id)
		if session:
			session.username = user.username

	return RedirectResponse(url="/settings#account", status_code=303)

@router.post("/settings/profile")
def update_player_profile(
    request: Request,
    db: Session = Depends(get_db),
    # Numeric/Single Selects
    birth_year: int = Form(None),
    region: str = Form(None),
    # Checkbox Groups
    languages: List[str] = Form([]),
    platforms: List[str] = Form([]),
    playtime: List[str] = Form([]),
    # Text Fields
    steam: str = Form(None),
    discord: str = Form(None),
    bio: str = Form(None) # Added this as it's usually in the profile section
):
	"""
	Update the current player's profile information.

	:param request: The incoming request containing the updated profile data in JSON format.
	:param birth_year: The player's birth year. Optional.
	:param region: The player's region. Optional.
	:param languages: A list of languages the player speaks. Optional.
	:param platforms: A list of gaming platforms the player uses. Optional.
	:param playtime: A list of playtime preferences (e.g. "weekdays", "weekends", "evenings"). Optional.
	:param steam: The player's Steam profile URL. Optional.
	:param discord: The player's Discord handle. Optional.
	:param bio: A short biography or description about the player. Optional.
	:raises HTTPException: 401 if not authenticated, 400 if the input data is invalid (e.g. birth year out of range).
	:return: A redirect response to the profile settings page on success.
	"""
	user = get_user(request, db)
	if not user:
		raise HTTPException(status_code=401, detail="Not authenticated")
	
	try:
		if bio is not None:
			user.profile.bio = bio

		if birth_year is not None:
			birth_year_error = validate_birth_year(birth_year)
			if birth_year_error:
				raise HTTPException(status_code=400, detail=birth_year_error)
			user.profile.birth_year = birth_year

		if region is not None:
			# find the region by name
			db_region = db.query(Region).filter(Region.name == region).first()
			if not db_region:
				raise HTTPException(status_code=400, detail="Invalid region")
			
			user.profile.region = db_region

		if languages is not None:
			# fetch Language objects matching the provided names
			selected_languages = db.query(Language).filter(Language.name.in_(languages)).all()
			# replace the collection
			user.languages = selected_languages
		
		if platforms is not None:
			selected_platforms = db.query(Platform).filter(Platform.name.in_(platforms)).all()
			user.platforms = selected_platforms

		if playtime:
			selected_playtimes = db.query(Playtime).filter(Playtime.name.in_(playtime)).all()
			user.playtimes = selected_playtimes

		if steam is not None:
			# TODO: steam url validation
			user.profile.steam_url = steam

		if discord is not None:
			user.profile.discord = discord
		
		db.commit()
	except Exception as e:
		db.rollback()
		raise e

	return RedirectResponse(url="/settings#profile", status_code=303)

@router.post("/settings/visibility")
def update_player_privacy(
	request: Request,
    db: Session = Depends(get_db),
	visibility: str = Form(...)
):
	"""
	Update the current player's profile privacy setting.

	:param request: The incoming request containing the updated privacy setting.
	:param db: The database session for querying and updating the player's profile.
	:param visibility: A string indicating the desired privacy level ("public" or "friends").
	:raises HTTPException: 401 if not authenticated, 400 if the visibility value is invalid.
	:return: A redirect response to the privacy settings page on success.
	"""
	user = get_user(request, db)
	if not user:
		raise HTTPException(status_code=401, detail="Not authenticated")
	
	if visibility not in ["public", "friends"]:
		raise HTTPException(status_code=400, detail="Invalid privacy setting")
	
	if visibility == "public":
		user.profile.private = False
	else:
		user.profile.private = True

	db.commit()

	return RedirectResponse(url="/settings#visibility", status_code=303)
	
@router.post("/settings/avatar")
def update_player_avatar():
	# TODO: avatar upload handling
	# - receive the uploaded file
	# - validate file type and size
	# - 128x128 cropping/resizing (if necessary) and convert to JPG
	# - save the file to static/img/profiles/{player_id}.jpg (overwrite if exists)
	# - update the player's profile to reference the new avatar path
	pass

