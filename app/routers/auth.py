from fastapi import APIRouter, HTTPException

router = APIRouter(prefix="/api/auth", tags=["auth"])


def get_auth_mode_stub() -> str:
	"""Return the planned authentication mode for future implementation."""
	return "session"


@router.post("/register")
def register_stub():
	raise HTTPException(status_code=501, detail="TODO: implement registration flow")


@router.post("/login")
def login_stub():
	raise HTTPException(status_code=501, detail="TODO: implement session login flow")


@router.post("/logout")
def logout_stub():
	raise HTTPException(status_code=501, detail="TODO: implement session logout flow")
