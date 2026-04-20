from fastapi import APIRouter, Depends, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.auth.sessions import get_current_user, get_optional_user
from app.auth.validation import (
	validate_hardware,
	validate_languages,
	validate_region,
	VALID_REGIONS,
	VALID_LANGUAGES,
	VALID_HARDWARE,
)
from app.database import get_db
from app.models import Player

router = APIRouter(prefix="/players", tags=["players"])
templates = Jinja2Templates(directory="templates")


@router.get("/{username}", response_class=HTMLResponse)
def get_player_profile(
	username: str,
	request: Request,
	db: Session = Depends(get_db),
	current_user: dict | None = Depends(get_optional_user),
):
	player = db.query(Player).filter(Player.username == username).first()
	if not player:
		raise HTTPException(status_code=404, detail=f"Player '{username}' not found.")

	is_own_profile = current_user is not None and current_user["username"] == username
	languages = player.language.split(",") if player.language else []

	return templates.TemplateResponse(
		request=request,
		name="profile.html",
		context={
			"player": player,
			"languages": languages,
			"is_own_profile": is_own_profile,
			"current_user": current_user,
		},
	)


@router.get("/{username}/edit", response_class=HTMLResponse)
def get_edit_profile(
	username: str,
	request: Request,
	db: Session = Depends(get_db),
	current_user: dict = Depends(get_current_user),
):
	if current_user["username"] != username:
		raise HTTPException(status_code=403, detail="You can only edit your own profile.")

	player = db.query(Player).filter(Player.username == username).first()
	if not player:
		raise HTTPException(status_code=404, detail="Player not found.")

	languages = player.language.split(",") if player.language else []

	return templates.TemplateResponse(
		request=request,
		name="profile_edit.html",
		context={
			"player": player,
			"languages": languages,
			"valid_regions": sorted(VALID_REGIONS),
			"valid_languages": sorted(VALID_LANGUAGES),
			"valid_hardware": sorted(VALID_HARDWARE),
			"current_user": current_user,
		},
	)


@router.post("/{username}/edit", response_class=HTMLResponse)
def post_edit_profile(
	username: str,
	request: Request,
	bio: str = Form(default=""),
	region: str = Form(default=""),
	languages: list[str] = Form(default=[]),
	hardware_platform: str = Form(default=""),
	db: Session = Depends(get_db),
	current_user: dict = Depends(get_current_user),
):
	if current_user["username"] != username:
		raise HTTPException(status_code=403, detail="You can only edit your own profile.")

	player = db.query(Player).filter(Player.username == username).first()
	if not player:
		raise HTTPException(status_code=404, detail="Player not found.")

	errors = []

	if region:
		err = validate_region(region)
		if err:
			errors.append(err)

	if languages:
		err = validate_languages(languages)
		if err:
			errors.append(err)

	if hardware_platform:
		err = validate_hardware(hardware_platform)
		if err:
			errors.append(err)

	if errors:
		return templates.TemplateResponse(
			request=request,
			name="profile_edit.html",
			context={
				"player": player,
				"languages": languages,
				"valid_regions": sorted(VALID_REGIONS),
				"valid_languages": sorted(VALID_LANGUAGES),
				"valid_hardware": sorted(VALID_HARDWARE),
				"current_user": current_user,
				"error": " ".join(errors),
			},
		)

	player.bio = bio or None
	player.region = region or None
	player.language = ",".join(languages) if languages else None
	player.hardware_platform = hardware_platform or None

	db.commit()

	return RedirectResponse(url=f"/players/{username}", status_code=302)
