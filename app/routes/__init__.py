"""API routes."""

from app.routes.health import router as health_router
from app.routes.candidates import router as candidates_router

__all__ = [
    "health_router",
    "candidates_router"
]
