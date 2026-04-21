from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.auth.hashing import hash_password, verify_password
from app.auth.sessions import create_session, delete_session
from app.auth.validation import validate_birth_year, validate_password, validate_username
from app.database import get_db
from app.models import Player

router = APIRouter(prefix="", tags=["auth"])
templates = Jinja2Templates(directory="templates")

# Registration page router
@router.get("/register", response_class=HTMLResponse)
def get_register(request: Request):
	return templates.TemplateResponse(request=request, name="auth/register.html")

@router.post("/register", response_class=HTMLResponse)
def post_register(
	request: Request,
	username: str = Form(...),
	password: str = Form(...),
	birth_year: int = Form(...),
	db: Session = Depends(get_db),
):
	username_error = validate_username(username)
	if username_error:
		return templates.TemplateResponse(
			request=request, name="auth/register.html", context={"error": username_error}
		)

	password_error = validate_password(password)
	if password_error:
		return templates.TemplateResponse(
			request=request, name="auth/register.html", context={"error": password_error}
		)

	age_error = validate_birth_year(birth_year)
	if age_error:
		return templates.TemplateResponse(
			request=request, name="auth/register.html", context={"error": age_error}
		)

	existing = db.query(Player).filter(Player.username == username).first()
	if existing:
		return templates.TemplateResponse(
			request=request,
			name="auth/register.html",
			context={"error": "That username is already taken."},
		)

	try:
		new_player = Player(
			username=username,
			password_hash=hash_password(password),
			birth_year=birth_year,
		)
		db.add(new_player)
		db.commit()
		db.refresh(new_player)
	except Exception as e:
		db.rollback()
		print("Error creating user:")
		print(e)
		return templates.TemplateResponse(
			request=request,
			name="auth/register.html",
			context={"error": "Something went wrong. Please try again."},
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
	return templates.TemplateResponse(request=request, name="auth/login.html")


@router.post("/login", response_class=HTMLResponse)
def post_login(
	request: Request,
	username: str = Form(...),
	password: str = Form(...),
	db: Session = Depends(get_db),
):
	_generic_error = "Username or password is incorrect."

	player = db.query(Player).filter(Player.username == username).first()
	if not player or not verify_password(password, player.password_hash):
		return templates.TemplateResponse(
			request=request, name="auth/login.html", context={"error": _generic_error}
		)

	session_id = create_session(player.id, player.username)
	response = RedirectResponse(url=f"/profile/{player.username}", status_code=302)
	response.set_cookie(
		key="session_id",
		value=session_id,
		httponly=True,
		samesite="lax",
		secure=False,
		max_age=86400,
	)
	return response

# Logout router
@router.post("/logout")
def post_logout(request: Request):
	session_id = request.cookies.get("session_id")
	if session_id:
		delete_session(session_id)

	response = RedirectResponse(url="/login", status_code=302)
	response.delete_cookie(key="session_id")
	return response

# def register_stub():
# raise HTTPException(status_code=501, detail="TODO: implement registration flow")

