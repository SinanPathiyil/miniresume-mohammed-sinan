"""
Main FastAPI application module.
Entry point for the Mini Resume Collector API.
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.routes import health_router, candidates_router
from app.middleware import add_error_handlers
from app.utils.logger import setup_logging, get_logger

# Set up logging
setup_logging()
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan context manager.
    Handles startup and shutdown events.
    """
    # Startup
    logger.info("="*60)
    logger.info(f"Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    logger.info(f"Debug Mode: {settings.DEBUG}")
    logger.info(f"Upload Directory: {settings.UPLOAD_DIR}")
    logger.info(f"Max File Size: {settings.MAX_FILE_SIZE / (1024*1024):.2f} MB")
    logger.info(f"Allowed Extensions: {', '.join(settings.ALLOWED_EXTENSIONS)}")
    logger.info("="*60)
    
    yield
    
    # Shutdown
    logger.info("="*60)
    logger.info(f"Shutting down {settings.APP_NAME}")
    logger.info("="*60)


# Create FastAPI application instance
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="""
    ## Mini Resume Collector API
    
    A production-ready REST API for managing candidate resumes with comprehensive validation and error handling.
    
    ### Features
    
    * **Resume Upload**: Upload candidate resumes with metadata (PDF/DOC/DOCX)
    * **Data Validation**: Comprehensive input validation using Pydantic
    * **Search & Filter**: Find candidates by skills, experience, and graduation year
    * **CRUD Operations**: Complete create, read, update, and delete functionality
    * **Error Handling**: Detailed error messages with proper HTTP status codes
    * **Logging**: Structured logging for monitoring and debugging
    
    ### File Upload Requirements
    
    * **Formats**: PDF, DOC, DOCX
    * **Maximum Size**: 10 MB
    * **Validation**: Automatic file type and size validation
    
    ### API Capabilities
    
    * Health check endpoint for service monitoring
    * Upload resumes with complete candidate information
    * List all candidates with advanced filtering options
    * Retrieve individual candidate details by ID
    * Delete candidates and associated files
    
    ### Error Handling
    
    All endpoints return consistent error responses with:
    * Error type classification
    * Descriptive error messages
    * Detailed validation information
    * Timestamp of error occurrence
    
    ### Technology Stack
    
    * **Framework**: FastAPI
    * **Validation**: Pydantic v2
    * **Storage**: In-memory (thread-safe)
    * **File Handling**: Secure UUID-based naming
    * **Logging**: Structured logging with file rotation
    """,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    contact={
        "name": "Mini Resume Collector API",
        "email": "support@example.com"
    },
    license_info={
        "name": "MIT",
        "url": "https://opensource.org/licenses/MIT"
    }
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add error handlers
add_error_handlers(app)

# Include routers
app.include_router(health_router)
app.include_router(candidates_router)

logger.info("Application initialized successfully")


if __name__ == "__main__":
    import uvicorn
    
    logger.info("Starting development server...")
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        log_level="info"
    )
