from fastapi.testclient import TestClient

from main import create_app

client = TestClient(create_app())


def test_home_page_renders_stub_template() -> None:
	"""Example test: verify the Jinja2 home page is wired correctly."""
	response = client.get("/")

	assert response.status_code == 200
	assert "Skeleton Ready" in response.text


def test_auth_register_get_returns_200() -> None:
	"""Auth register route is fully implemented and returns the registration form."""
	response = client.get("/register")

	assert response.status_code == 200
	assert "register" in response.text.lower() or "username" in response.text.lower()



# def test_auth_register_stub_returns_501() -> None:
#	"""Example test: API stubs should be explicit not-implemented handlers."""
#	response = client.post("/api/auth/register")
#
#	assert response.status_code == 501
#	assert response.json()["detail"].startswith("TODO:")


def test_search_scope_stub_per_game_only() -> None:
	"""Example test: per-game search stub endpoint is present and not implemented."""
	response = client.get("/api/search/games/counterstrike/players", params={"q": "ace"})

	assert response.status_code == 501
	assert "counterstrike" in response.json()["detail"]
