"""
Generic exception handling for HTTP errors to render user-friendly error pages.
"""

from fastapi import Request

from app.database import SessionLocal
from app.routers.pages._shared import templates, create_profile_context

def http_exception_handler(request: Request, exc: Exception):
	"""Custom handler for HTTP exceptions to render a user-friendly error page."""

	profile = None
	try:
		with SessionLocal() as db:
			profile = create_profile_context(db, request)
	except:
		profile = None

	context = {
		"request": request,
		"status_code": getattr(exc, "status_code", 500),
		"message": getattr(exc, "detail", "An unexpected error occurred."),
		"profile": profile
	}

	return templates.TemplateResponse(
		request=request,
		name="error.html",
		context=context,
		status_code=getattr(exc, "status_code", 500)
	)