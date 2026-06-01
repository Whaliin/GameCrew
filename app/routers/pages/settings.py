"""
Page route for user settings page, where users can update their profile information
"""

from datetime import date

from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session

from app.auth.sessions import get_user
from app.database import get_db
from app.models import Language, Platform, Playtime, Region
from app.routers.pages._shared import templates, create_profile_context

router = APIRouter(prefix="/settings", tags=["pages"])

@router.get("", response_class=HTMLResponse)
def settings(request: Request, db: Session = Depends(get_db)):
	"""Get the settings page."""
	context = {}

	current_user = get_user(request, db)
	if not current_user:
		# If somehow we got here without a user, redirect to login.
		return RedirectResponse(url="/login", status_code=302)
	
	context["profile"] 		= create_profile_context(db, request, current_user)

	# attach existing profile information to the context to pre-fill the form fields
	context["current"] = {
		"region": current_user.profile.region.name if current_user.profile.region else None,
		"birth_year": current_user.profile.birth_year,
		"private": current_user.profile.private,
		"bio": current_user.profile.bio,
		"steam": current_user.profile.steam_url if current_user.profile.steam_url else "",
		"discord": current_user.profile.discord if current_user.profile.discord else "",
		"riot": current_user.profile.riot_id if current_user.profile.riot_id else "",
		"platforms": [pf.name for pf in current_user.platforms] if current_user.platforms else [],
		"playtime": [pt.name for pt in current_user.playtimes] if current_user.playtimes else [],
		"languages": [lang.name for lang in current_user.languages] if current_user.languages else [],
	}

	context["regions"]   = [r[0] for r in db.query(Region.name).distinct().all()]
	context["platforms"] = [r[0] for r in db.query(Platform.name).distinct().all()]
	context["playtimes"] = [r[0] for r in db.query(Playtime.name).distinct().all()]
	context["languages"] = [r[0] for r in db.query(Language.name).distinct().all()]

	context["max_birth_date"] = f"{(date.today().replace(year=date.today().year - 18)).isoformat()}"

	return templates.TemplateResponse(request=request, name="settings.html", context=context)