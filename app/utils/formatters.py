"""
Utility functions for formatting data for templates and API responses.
"""

from datetime import datetime

def map_age_range(birth_year: int) -> str:
	"""Map birth year to a coarse age range used in templates.
	
	:param birth_year: The birth year to map.
	:return: A string representing the age range category.
	"""
	age = datetime.now().year - birth_year
	if age < 18:
		return "Under 18" # This case should be prevented by validation
	if age <= 25:
		return "18-25"
	if age <= 35:
		return "26-35"
	if age <= 45:
		return "36-45"
	return "45+"