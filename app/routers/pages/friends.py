"""
Page router for the friends list page.
"""

from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session

from app.auth.sessions import get_user
from app.database import get_db
from app.models import PlayerProfile
from app.routers.pages._shared import templates, create_profile_context, get_pending_friend_requests, is_friend, get_friends
from app.utils.assets import get_avatar_url

router = APIRouter(prefix="/friends", tags=["pages"])

@router.get("/", response_class=HTMLResponse)
def friends_page(request: Request, db: Session = Depends(get_db)):
	"""Get the friends page."""
	context = {}

	current_user = get_user(request, db)

	if not current_user:
		# If somehow we got here without a user, redirect to login.
		return RedirectResponse(url="/login", status_code=302)

	context["profile"] = create_profile_context(db, request, current_user)

	# Get the users friends and pending friend requests
	friends = get_friends(db, current_user)
	friendships_pending = get_pending_friend_requests(db, current_user)

	for friend in friends:
		friend.avatar_url = get_avatar_url(friend.id)

	pending_requests = []
	for friendship in friendships_pending:
		# get the player profile of each sender of the pending requests (Friendship)
		sender_profile = db.query(PlayerProfile).filter(PlayerProfile.player_id == friendship.sender_id).first()
		if sender_profile:
			pending_requests.append({
				"username": sender_profile.player.username,
				"avatar_url": get_avatar_url(sender_profile.player_id),
				"platform": ", ".join([pf.name for pf in sender_profile.player.platforms]) if sender_profile.player.platforms else "N/A",
			})

	context["friends"] = friends
	context["pending_requests"] = pending_requests

	return templates.TemplateResponse(request=request, name="friends.html", context=context)