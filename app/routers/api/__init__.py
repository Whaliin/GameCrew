"""
Package for API routes (JSON responses)
"""

from fastapi import APIRouter

router = APIRouter(prefix="/api", tags=["api"])

from .games import router as games_router
from .players import router as players_router
from .profile import router as profile_router
from .search import router as search_router

router.include_router(games_router)
router.include_router(players_router)
router.include_router(profile_router)
router.include_router(search_router)