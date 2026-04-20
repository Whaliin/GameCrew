from app import create_app
from app.database import init_database_stub

app = create_app()


def startup() -> None:
	"""Run startup-time scaffold hooks for local development."""
	init_database_stub()


startup()