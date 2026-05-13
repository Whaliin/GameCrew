"""
Package for page routes (HTML responses)
"""


from fastapi import APIRouter

router = APIRouter(tags=["pages"])

from .home import router as home_router
from .game import router as game_router
from .profile import router as profile_router
from .settings import router as settings_router
from .friends import router as friends_router

router.include_router(home_router)
router.include_router(game_router)
router.include_router(profile_router)
router.include_router(settings_router)
router.include_router(friends_router)