import re
from datetime import date

from sqlalchemy.orm import Session

from app.models import Language, Platform, Region

# regular expression for allowed usernames:
# - only letters, numbers, underscores
_USERNAME_RE = re.compile(r'^[a-zA-Z0-9_]+$')

# These should be fetched from the database, and we may have to remove this entire validation.

# Check that username is valid according to guidelines
def validate_username(username: str) -> str | None:
	"""Return an error string if username is invalid, or None if valid."""
	if len(username) < 3 or len(username) > 50:
		return "Username must be 3–50 characters."
	if not _USERNAME_RE.match(username):
		return "Username may only contain letters, numbers, or underscore."
	return None

# Check that password is valid according to guidelines
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

# Check the user's age via year of birth
def validate_birth_year(birth_year: int) -> str | None:
	"""Return an error string if user is under 18, or None if valid."""
	current_year = date.today().year
	if current_year - birth_year < 18:
		return "You must be at least 18 years old to register."
	if birth_year < 1920 or birth_year > current_year:
		return "Please enter a valid birth year."
	return None

# Check User's region is valid from the choices
def validate_region(db: Session, region: str) -> str | None:
	# Fetch valid regions from the database
	# For each region, get the name but since the query returns a list of tuples we need to loop again
	valid_regions = [r[0] for r in db.query(Region.name).all()]
	if region not in valid_regions:
		return f"Invalid region. Choose from: {', '.join(sorted(valid_regions))}"
	return None

# Check User's language is valid and less or equal to 3
def validate_languages(db: Session, languages: list[str]) -> str | None:
	if len(languages) > 3:
		return "You may only select up to 3 languages."
	
	# Fetch valid languages from the database
	valid_languages = [l[0] for l in db.query(Language.name).all()]

	invalid = [l for l in languages if l not in valid_languages]
	if invalid:
		return f"Invalid language(s): {', '.join(invalid)}"
	return None

# Checks if the platform is valid 
def validate_hardware(db: Session, hardware: str) -> str | None:
	valid_platforms = [p[0] for p in db.query(Platform.name).all()]
	if hardware not in valid_platforms:
		return f"Invalid platform. Choose from: {', '.join(sorted(valid_platforms))}"
	return None