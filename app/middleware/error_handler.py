"""
Global error handler middleware.
Provides consistent error responses across the application.
"""

from datetime import datetime
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError

from app.utils.logger import get_logger
from app.utils.exceptions import (
    ApplicationError,
    CandidateNotFoundError,
    InvalidFileTypeError,
    FileSizeExceededError
)

logger = get_logger(__name__)


def add_error_handlers(app: FastAPI) -> None:
    """
    Add global error handlers to the FastAPI application.
    
    Args:
        app: FastAPI application instance
    """
    
    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        """Handle Pydantic validation errors."""
        errors = exc.errors()
        error_details = []
        
        for error in errors:
            field = " -> ".join(str(loc) for loc in error['loc'])
            error_details.append({
                "field": field,
                "message": error['msg'],
                "type": error['type']
            })
        
        logger.warning(f"Validation error on {request.url.path}: {error_details}")
        
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "error": "ValidationError",
                "message": "Request validation failed",
                "detail": error_details,
                "timestamp": datetime.now().isoformat()
            }
        )
    
    @app.exception_handler(ValueError)
    async def value_error_handler(request: Request, exc: ValueError):
        """Handle ValueError exceptions."""
        logger.warning(f"ValueError on {request.url.path}: {str(exc)}")
        
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "error": "ValueError",
                "message": str(exc),
                "timestamp": datetime.now().isoformat()
            }
        )
    
    @app.exception_handler(CandidateNotFoundError)
    async def candidate_not_found_handler(request: Request, exc: CandidateNotFoundError):
        """Handle candidate not found errors."""
        logger.warning(f"Candidate not found on {request.url.path}: {exc.message}")
        
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={
                "error": "CandidateNotFound",
                "message": exc.message,
                "timestamp": datetime.now().isoformat()
            }
        )
    
    @app.exception_handler(InvalidFileTypeError)
    async def invalid_file_type_handler(request: Request, exc: InvalidFileTypeError):
        """Handle invalid file type errors."""
        logger.warning(f"Invalid file type on {request.url.path}: {exc.message}")
        
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "error": "InvalidFileType",
                "message": exc.message,
                "detail": exc.detail,
                "timestamp": datetime.now().isoformat()
            }
        )
    
    @app.exception_handler(FileSizeExceededError)
    async def file_size_exceeded_handler(request: Request, exc: FileSizeExceededError):
        """Handle file size exceeded errors."""
        logger.warning(f"File size exceeded on {request.url.path}: {exc.message}")
        
        return JSONResponse(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            content={
                "error": "FileSizeExceeded",
                "message": exc.message,
                "detail": exc.detail,
                "timestamp": datetime.now().isoformat()
            }
        )
    
    @app.exception_handler(ApplicationError)
    async def application_error_handler(request: Request, exc: ApplicationError):
        """Handle generic application errors."""
        logger.error(f"Application error on {request.url.path}: {exc.message}")
        
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "error": "ApplicationError",
                "message": exc.message,
                "detail": exc.detail,
                "timestamp": datetime.now().isoformat()
            }
        )
    
    @app.exception_handler(Exception)
    async def generic_exception_handler(request: Request, exc: Exception):
        """Handle all unhandled exceptions."""
        logger.error(
            f"Unhandled exception on {request.url.path}: {str(exc)}",
            exc_info=True
        )
        
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "error": "InternalServerError",
                "message": "An unexpected error occurred",
                "timestamp": datetime.now().isoformat()
            }
        )
    
    logger.info("Global error handlers registered")
