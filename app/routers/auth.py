# ==================================
# Authentication and registration routes.
# ==================================

from datetime import date

from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.auth.hashing import hash_password, verify_password
from app.auth.sessions import create_session, delete_session, get_user
from app.auth.validation import validate_birth_year, validate_password, validate_region, validate_username
from app.database import get_db
from app.models import Player, PlayerGameProfile, PlayerProfile, Region

router = APIRouter(prefix="", tags=["auth"])
templates = Jinja2Templates(directory="templates")


def register_context(db: Session, error: str | None = None, form_data: dict | None = None) -> dict:
	"""Build consistent template context for register page renders."""
	context: dict = {
		# Get regions from the database to populate the region dropdown in the form.
		# We order by name, but ideally we would want to group them by continent.
		"regions": db.query(Region).order_by(Region.name).all(),
		"max_birth_year": date.today().year - 18,
		"form_data": form_data or {},
	}

	# Attach the error message to context if provided so it can be displayed in the template.
	if error:
		context["error"] = error
	return context

# Registration page router
@router.get("/register", response_class=HTMLResponse)
def get_register(request: Request, db: Session = Depends(get_db)):
	"""Registrations page first load router. Shows the form with no error message"""
	return templates.TemplateResponse(
		request=request,
		name="auth/register.html",
		context=register_context(db),
	)

@router.post("/register", response_class=HTMLResponse)
def post_register(
	request: Request,
	username: str = Form(...),
	password: str = Form(...),
	birth_year: int = Form(...),
	region_id: int = Form(...),
	db: Session = Depends(get_db),
):
	"""Handle user registration form submission.
	This route only accepts the birth year and region ID as these are considered basic/core profile information."""
	
	# Create a form data dict to pre-fill the next form render with the user's previous input if validation fails.
	form_data = {
		"username": username,
		"birth_year": birth_year,
		"region_id": region_id,
	}

	# Validate username
	username_error = validate_username(username)
	if username_error:
		return templates.TemplateResponse(
			request=request,
			name="auth/register.html",
			context=register_context(db, username_error, form_data),
		)

	# Validate password
	password_error = validate_password(password)
	if password_error:
		return templates.TemplateResponse(
			request=request,
			name="auth/register.html",
			context=register_context(db, password_error, form_data),
		)

	# Validate birth year
	age_error = validate_birth_year(birth_year)
	if age_error:
		return templates.TemplateResponse(
			request=request,
			name="auth/register.html",
			context=register_context(db, age_error, form_data),
		)

	# Validate region ID
	region_error = validate_region(db, region_id)
	if region_error:
		return templates.TemplateResponse(
			request=request,
			name="auth/register.html",
			context=register_context(db, region_error, form_data),
		)

	# Check if the username is already taken
	existing = db.query(Player).filter(Player.username == username).first()
	if existing:
		return templates.TemplateResponse(
			request=request,
			name="auth/register.html",
			context=register_context(db, "That username is already taken.", form_data),
		)

	try:
		# First add the player object to get an ID
		new_player = Player(
			username=username,
			password_hash=hash_password(password)
		)
		db.add(new_player)
		db.flush()  # Flush to assign an ID to new_player

		# Add the profile with the player ID and the region FK
		new_profile = PlayerProfile(
			player_id=new_player.id, 
			region_id=region_id, 
			birth_year=birth_year
		)
		db.add(new_profile)
		
		db.commit()
		db.refresh(new_player)
	except Exception as e:
		# On any exception, rollback the transaction
		db.rollback()
		print("Error creating user:")
		print(e)
		return templates.TemplateResponse(
			request=request,
			name="auth/register.html",
			context=register_context(db, "Something went wrong. Please try again.", form_data),
		)

	session_id = create_session(new_player.id, new_player.username)
	response = RedirectResponse(url=f"/profile/{username}", status_code=302)
	response.set_cookie(
		key="session_id",
		value=session_id,
		httponly=True,
		samesite="lax",
		secure=False,
		max_age=86400,
	)
	return response

# Login page router
@router.get("/login", response_class=HTMLResponse)
def get_login(request: Request):
	"""Login page router with no special context."""
	return templates.TemplateResponse(request=request, name="auth/login.html")

# NOAUTH flag to bypass auth for dev mode
NOAUTH = True

@router.post("/login", response_class=HTMLResponse)
def post_login(
	request: Request,
	username: str = Form(...),
	password: str = Form(...),
	db: Session = Depends(get_db),
):
	"""Handle user login form submission."""

	player = db.query(Player).filter(Player.username == username).first()
	if not player or (not NOAUTH and not verify_password(password, player.password_hash)):
		# Invalid credentials - re-render the login page with an error message. 
		# We don't specify which field is wrong for security reasons.
		return templates.TemplateResponse(
			request=request, name="auth/login.html", context={"error": "Username or password is incorrect."}
		)

	# Create a session in memory
	session_id = create_session(player.id, player.username)
	# Redirect to the index page
	response = RedirectResponse(url="/", status_code=302)
	# Set the session cookie with appropriate flags for security and expiration
	response.set_cookie(
		key="session_id",
		value=session_id,
		httponly=True,
		samesite="lax",
		secure=False,
		max_age=86400,
	)
	return response

@router.post("/logout")
def post_logout(request: Request):
	"""Handle user logout by deleting the session and clearing the cookie."""
	session_id = request.cookies.get("session_id")
	if session_id:
		delete_session(session_id)

	response = RedirectResponse(url="/login", status_code=302)
	response.delete_cookie(key="session_id")
	return response

@router.delete("/delete-account")
def delete_account(request: Request, db: Session = Depends(get_db)):
	"""Handle account deletion by removing the user from the database and clearing their session. 
	We assume in this route that the user has already confirmed their intention to delete their account."""
	session = get_user(request, db)
	if session is None:
		return RedirectResponse(url="/login", status_code=302)

	try:
		player = db.query(Player).filter(Player.id == session.player_id).first()
		
		# This should never happen since the user is authenticated, but we check just in case to avoid errors or unintended behavior.
		if not player:
			return RedirectResponse(url="/login", status_code=302)
		
		# Delete the player's game profiles first due to foreign key constraints
		db.query(PlayerGameProfile).filter(PlayerGameProfile.player_id == player.id).delete()

		# Delete the players profile
		db.query(PlayerProfile).filter(PlayerProfile.player_id == player.id).delete()

		# Finally, delete the player
		db.delete(player)

		# TODO: Do we need to delete junction table entries as well?
		# Ideally cascade delete would solve this. But I am not sure if SQLAlchemy does it automatically.

		db.commit()

		# Delete the users session and clear the cookie to log them out after deleting their account.
		delete_session(session.session_id)
		response = RedirectResponse(url="/", status_code=302)
		response.delete_cookie(key="session_id")
		return response
	except Exception as e:
		print("Error deleting account:")
		print(e)
		db.rollback()
		return templates.TemplateResponse(
			request=request,
			name="profile.html",
			context={"error": "Something went wrong while deleting your account. Please try again."},
		)
	
	