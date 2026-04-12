import re

_USERNAME_RE = re.compile(r'^[a-zA-Z0-9_]+$')


def validate_username(username: str) -> str | None:
    """Return an error string if username is invalid, or None if valid.

    Valid: 3–50 characters, alphanumeric + underscore only.
    """
    if len(username) < 3 or len(username) > 50:
        return "Username must be 3–50 characters and contain only letters, numbers, or underscores."
    if not _USERNAME_RE.match(username):
        return "Username must be 3–50 characters and contain only letters, numbers, or underscores."
    return None


def validate_password(password: str) -> str | None:
    """Return an error string if password is invalid, or None if valid.

    Valid: at least 6 characters.
    """
    if len(password) < 6:
        return "Password must be at least 6 characters."
    return None
