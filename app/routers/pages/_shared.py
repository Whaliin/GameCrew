"""
Shared utilities for page routes.
These are helper functions used across multiple page routes
"""

from fastapi import Request
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.auth.sessions import get_user
from app.models import Friendship, Game, Player, PlayerGameProfile, PlayerProfile
from app.utils.assets import get_avatar_url, get_game_image_url

templates = Jinja2Templates(directory="templates")

def _force_player_object(user: Player | PlayerProfile | None) -> Player | None:
	"""Utility function to ensure we have a Player object regardless of whether we were given a Player or PlayerProfile."""

	if isinstance(user, Player):
		return user
	if isinstance(user, PlayerProfile):
		return user.player
	
	return None

def get_friend_requests_count(db: Session, user: PlayerProfile | Player) -> int:
	"""Return the count of pending friend requests for the current user."""
	user = _force_player_object(user)
	if not user:
		return 0

	return db.query(Friendship).filter(
		Friendship.receiver_id == user.id,
		Friendship.accepted == False
	).count()

def get_pending_friend_requests(db: Session, user: PlayerProfile | Player) -> list[Friendship]:
	"""Return a list of pending friend requests for the current user."""
	user = _force_player_object(user)
	if not user:
		return []
	
	return db.query(Friendship).filter(
		Friendship.receiver_id == user.id,
		Friendship.accepted == False
	).all()

def get_sent_requests(db: Session, user: PlayerProfile | Player) -> list[Friendship]:
	"""Return a list of friend requests sent by the current user that are still pending."""
	user = _force_player_object(user)
	if not user:
		return []

	return db.query(Friendship).filter(
		Friendship.sender_id == user.id,
		Friendship.accepted == False
	).all()

def is_friend(db: Session, user1: Player, user2: Player) -> bool:
	"""Check if two users are friends."""
	user1 = _force_player_object(user1)
	user2 = _force_player_object(user2)
	if not user1 or not user2:
		return False
	
	return db.query(Friendship).filter(
		((Friendship.sender_id == user1.id) & (Friendship.receiver_id == user2.id)) |
		((Friendship.sender_id == user2.id) & (Friendship.receiver_id == user1.id)),
		Friendship.accepted == True
	).first() is not None

def get_friends(db: Session, user: Player) -> list[Player]:
	"""Return a list of friends for the current user."""
	user = _force_player_object(user)
	if not user:
		return []
	
	# query for players
	# join on friendships where (sender_id or receiver_id is the user) and accepted is true
	# distinct to deduplicate
	# exclude the user themselves from results
	return db.query(Player).join(Friendship, ((Friendship.receiver_id == Player.id) | (Friendship.sender_id == Player.id))).filter(
		((Friendship.sender_id == user.id) | (Friendship.receiver_id == user.id)),
		Friendship.accepted == True,
		Player.id != user.id
	).distinct().all()

def create_profile_context(db: Session, request: Request, user_session: Player | None = None) -> dict | None:
	"""Create a consistent context for rendering the navbar across different pages."""
	# If user_session is not provided, attempt to get it from the request. This allows us to reuse this function in contexts where we may already have the session data available, such as within the auth router after login.
	if not user_session:
		user_session = get_user(request, db)
	
	if not user_session:
		return None
	
	# Get the users favorite games
	user_favorite_games = db.query(Game).join(PlayerGameProfile, PlayerGameProfile.game_id == Game.id).filter(PlayerGameProfile.player_id == user_session.id).all()
	
	# Append image URLs to the favorite games
	for game in user_favorite_games:
		game.image_url = get_game_image_url(game.slug)

	profile_context = {
		"username": user_session.username,
		"avatar_url": get_avatar_url(user_session.id),
		"pending_requests": get_friend_requests_count(db, user_session),
		"favorite_games": user_favorite_games,
		"platforms": [pf.name for pf in user_session.platforms] if user_session.platforms else [],
		"playtimes": [pt.name for pt in user_session.playtimes] if user_session.playtimes else [],
		"languages": [lang.name for lang in user_session.languages] if user_session.languages else [],
		"region": user_session.profile.region.name if user_session.profile.region else None,
	}

	return profile_context