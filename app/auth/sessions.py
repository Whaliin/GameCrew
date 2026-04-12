import secrets
from fastapi import Request
from fastapi.responses import RedirectResponse

# In-memory session store: { session_id: {"player_id": int, "username": str} }
_sessions: dict[str, dict] = {}


def create_session(player_id: int, username: str) -> str:
    """Generate a session ID, store the session, and return the ID."""
    session_id = secrets.token_urlsafe(32)
    _sessions[session_id] = {"player_id": player_id, "username": username}
    return session_id


def get_session(session_id: str) -> dict | None:
    """Return session data or None if not found."""
    return _sessions.get(session_id)


def delete_session(session_id: str) -> None:
    """Remove a session from the store."""
    _sessions.pop(session_id, None)

def get_current_user(request: Request) -> dict:
    """FastAPI dependency — reads session_id cookie, looks up session.
    Raises RedirectResponse to /login if unauthenticated."""
    session_id = request.cookies.get("session_id")
    if session_id:
        session = get_session(session_id)
        if session:
            return session
    raise RedirectResponse("/login")


def get_optional_user(request: Request) -> dict | None:
    """FastAPI dependency — returns session data or None (no redirect)."""
    session_id = request.cookies.get("session_id")
    if session_id:
        return get_session(session_id)
    return None
