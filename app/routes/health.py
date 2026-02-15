"""
Health check endpoint.
Provides system status and version information.
"""

from datetime import datetime
from fastapi import APIRouter, status

from app.models.schemas import HealthResponse
from app.config import settings
from app.utils.logger import get_logger

logger = get_logger(__name__)

router = APIRouter(tags=["Health"])


@router.get(
    "/health",
    response_model=HealthResponse,
    status_code=status.HTTP_200_OK,
    summary="Health Check",
    description="""
    Check the health status of the API service.
    
    This endpoint provides:
    - Service availability status
    - Current server timestamp
    - Application version information
    - Status message
    
    Use this endpoint to verify that the service is running and accessible.
    No authentication is required for this endpoint.
    """,
    responses={
        200: {
            "description": "Service is healthy and running",
            "content": {
                "application/json": {
                    "example": {
                        "status": "healthy",
                        "timestamp": "2026-02-15T20:46:55",
                        "version": "1.0.0",
                        "message": "Service is running"
                    }
                }
            }
        }
    }
)
async def health_check() -> HealthResponse:
    """
    Health check endpoint that returns the current status of the application.
    
    Returns:
        HealthResponse: Current health status with timestamp and version
    """
    logger.debug("Health check requested")
    
    return HealthResponse(
        status="healthy",
        timestamp=datetime.now(),
        version=settings.APP_VERSION,
        message="Service is running"
    )
