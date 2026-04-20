import re
from datetime import date

_USERNAME_RE = re.compile(r'^[a-zA-Z0-9_]+$')

VALID_REGIONS = {"EU", "NA", "SA", "AS", "OC", "AF", "ME"}
VALID_LANGUAGES = {"en", "sv", "es", "fr", "de", "pt", "ar", "zh", "ja", "ko", "ru", "tr"}
VALID_HARDWARE = {"PC", "PlayStation", "Xbox", "Nintendo Switch", "Mobile"}


def validate_username(username: str) -> str | None:
	"""Return an error string if username is invalid, or None if valid."""
	if len(username) < 3 or len(username) > 50:
		return "Username must be 3–50 characters."
	if not _USERNAME_RE.match(username):
		return "Username may only contain letters, numbers, or underscores."
	return None


def validate_password(password: str) -> str | None:
	"""Return an error string if password fails F-SEC-02 rules, or None if valid.

	Rules: min 10 chars, at least one uppercase, one lowercase, one digit, one special char.
	"""
	if len(password) < 10:
		return "Password must be at least 10 characters."
	if not re.search(r'[A-Z]', password):
		return "Password must contain at least one uppercase letter."
	if not re.search(r'[a-z]', password):
		return "Password must contain at least one lowercase letter."
	if not re.search(r'\d', password):
		return "Password must contain at least one digit."
	if not re.search(r'[^a-zA-Z0-9]', password):
		return "Password must contain at least one special character."
	return None


def validate_birth_year(birth_year: int) -> str | None:
	"""Return an error string if user is under 18, or None if valid."""
	current_year = date.today().year
	if current_year - birth_year < 18:
		return "You must be at least 18 years old to register."
	if birth_year < 1900 or birth_year > current_year:
		return "Please enter a valid birth year."
	return None


def validate_region(region: str) -> str | None:
	if region not in VALID_REGIONS:
		return f"Invalid region. Choose from: {', '.join(sorted(VALID_REGIONS))}"
	return None


def validate_languages(languages: list[str]) -> str | None:
	if len(languages) > 3:
		return "You may select up to 3 languages."
	invalid = [l for l in languages if l not in VALID_LANGUAGES]
	if invalid:
		return f"Invalid language(s): {', '.join(invalid)}"
	return None


def validate_hardware(hardware: str) -> str | None:
	if hardware not in VALID_HARDWARE:
		return f"Invalid platform. Choose from: {', '.join(sorted(VALID_HARDWARE))}"
	return None