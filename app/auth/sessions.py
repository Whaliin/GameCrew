import secrets
from fastapi import Request
from fastapi.responses import RedirectResponse

# In-memory session store: { session_id: {"player_id": int, "username": str} }

class UserSession:
	"""Represents a user session with player_id and username."""
	def __init__(self, player_id: int, username: str):
		self.player_id = player_id
		self.username = username

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

# Remove session
def delete_session(session_id: str) -> None:
	"""Remove a session from the store."""
	_sessions.pop(session_id, None)

# Couple session with user
def get_current_user(request: Request) -> UserSession | None:
	"""FastAPI dependency — reads session_id cookie, looks up session.
	Raises RedirectResponse to /login if unauthenticated."""
	session_id = request.cookies.get("session_id")
	if session_id:
		session = get_session(session_id)
		if session:
			return session
	raise RedirectResponse("/login")

def get_optional_user(request: Request) -> UserSession | None:
	"""FastAPI dependency — returns session data or None (no redirect)."""
	session_id = request.cookies.get("session_id")
	if session_id:
		return get_session(session_id)
	return None
