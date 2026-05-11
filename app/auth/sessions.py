import secrets
from fastapi import Request
from sqlalchemy.orm import Session

from app.models import Player

# In-memory session store: { session_id: {"player_id": int, "username": str} }

class UserSession:
	"""Represents a user session with player_id and username."""
	def __init__(self, player_id: int, username: str):
		self.player_id = player_id
		self.username = username

# The session store is a simple in-memory dictionary mapping session IDs to UserSession objects.
_sessions: dict[str, UserSession] = {}

# Begin a session
def create_session(player_id: int, username: str) -> str:
	"""Generate a session ID, store the session, and return the ID."""
	session_id = secrets.token_urlsafe(32)
	_sessions[session_id] = UserSession(player_id=player_id, username=username)
	return session_id

# Identify session
def get_session(session_id: str) -> UserSession | None:
	"""Return session data or None if not found."""
	return _sessions.get(session_id)

# Identify session (request based)
def get_session_id(request: Request) -> str | None:
	"""FastAPI dependency - returns session data or None (no redirect)."""
	return request.cookies.get("session_id")

# Remove session
def delete_session(session_id: str) -> None:
	"""Remove a session from the store."""
	_sessions.pop(session_id, None)

# Get the current user session, or None if not authenticated.
def get_optional_user(request: Request) -> UserSession | None:
	"""FastAPI dependency - returns session data or None (no redirect)."""
	session_id = request.cookies.get("session_id")
	if session_id:
		return get_session(session_id)
	return None

def get_user(request: Request, db: Session) -> Player | None:
	"""Get the Player object for the current session, or None if not authenticated."""
	session = get_optional_user(request)
	if session is None:
		return None
	
	return db.query(Player).filter(Player.id == session.player_id).first()