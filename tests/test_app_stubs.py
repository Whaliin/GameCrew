from fastapi.testclient import TestClient

from app import create_app

client = TestClient(create_app())


def test_home_page_renders_template() -> None:
	"""Verify the Jinja2 home page is wired correctly."""
	response = client.get("/")

	assert response.status_code == 200
	assert "Dina mest spelade" in response.text


def test_auth_register_get_returns_200() -> None:
	"""Auth register route is fully implemented and returns the registration form."""
	response = client.get("/register")

	assert response.status_code == 200
	assert "register" in response.text.lower() or "username" in response.text.lower()

def test_search_players_per_game_returns_results() -> None:
	"""Per-game search endpoint returns a successful payload."""
	response = client.get("/api/search/games/counterstrike/players", params={"q": "ace"})

	assert response.status_code == 200
	assert response.json()["game_slug"] == "counterstrike"
	assert isinstance(response.json()["results"], list)
