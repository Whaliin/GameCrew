import re
from datetime import date
from urllib.parse import urlparse

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
def validate_birth_year(birth_date: date) -> str | None:
	"""Return an error string if user is under 18, or None if valid."""
	current_year = date.today().year
	if birth_date > date.today().replace(year=current_year - 18):
		return "You must be at least 18 years old to register."
	if birth_date.year < 1920 or birth_date.year > current_year:
		return "Please enter a valid birth year."
	return None

# Check User's region is valid from the choices
def validate_region(db: Session, region_id: int) -> str | None:
	# Fetch valid regions from the database
	# For each region, get the name but since the query returns a list of tuples we need to loop again
	valid_regions = [r[0] for r in db.query(Region.id).all()]
	if region_id not in valid_regions:
		return "Invalid region. Choose a valid region ID from the dropdown."
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

	invalid = [h for h in hardware if h not in valid_platforms]
	if invalid:
		return f"Invalid platform(s): {', '.join(invalid)}"
	return None

_STEAM64_BASE = 76561197960265728

def validate_steam64(value: str) -> bool:
	value = value.strip()

	if not re.fullmatch(r'\d{17}', value):
		return False
	
	if int(value) < _STEAM64_BASE:
		return False
	
	return True
	
def validate_steam(value: str) -> str | None:
	value = value.strip()

	if not value:
		return None # Empty is allowed (for optional field)
	
	# Check if its a valid url
	try:
		url = urlparse(value)
		if url.scheme not in ('http', 'https'):
			return "Steam URL must start with http:// or https://"
		
		if 'steamcommunity.com' not in url.netloc:
			return "Steam URL must be from steamcommunity.com"
		
		# Check if the path contains /id/ or /profiles/ followed by a valid identifier
		path_parts = url.path.strip('/').split('/')
		if len(path_parts) != 2 or path_parts[0] not in ('id', 'profiles'):
			return "Steam URL must be in the format https://steamcommunity.com/id/yourname or https://steamcommunity.com/profiles/steamid"
		
		identifier = path_parts[1]
		if path_parts[0] == 'id':
			# Custom vanity URL, we can't validate the identifier format without calling the Steam API, so we'll just check it's non-empty and doesn't contain spaces
			if not identifier or ' ' in identifier:
				return "Invalid Steam vanity URL identifier."
		else:
			# SteamID64, validate it's a 17-digit number and above the minimum SteamID64 value
			if not validate_steam64(identifier):
				return "Invalid SteamID64 in URL."
	except Exception as e:
		return "Invalid Steam URL format."
	
	# All checks passed
	return None

def validate_riot(value: str) -> str | None:
	# Riot ID should have a name and then a tag separated by #
	value = value.strip()
	if not value:
		return None # Empty is allowed (for optional field)
	
	parts = value.split('#')
	if len(parts) != 2:
		return "Riot ID must be in the format Name#Tag"
	
	name, tag = parts
	if not name or not tag:
		return "Riot ID must have both a name and a tag."
	
	if len(tag) > 5:
		return "Riot ID tag must be 5 characters or less."
	
	return None

def validate_discord(value: str) -> str | None:
	# Discord username should be max 32 characters and can contain letters, numbers, underscores and periods.
	value = value.strip()
	if not value:
		return None # Empty is allowed (for optional field)
	
	if len(value) > 32:
		return "Discord username must be 32 characters or less."
	
	if not re.fullmatch(r'[a-zA-Z0-9_.]+', value):
		return "Discord username may only contain letters, numbers, underscores, or periods."

	return None