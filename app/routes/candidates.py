"""
Candidate management endpoints.
Provides CRUD operations for candidate resumes.
"""

from typing import List, Optional
from fastapi import APIRouter, UploadFile, File, Form, Depends, status, HTTPException

from app.models.schemas import CandidateCreate, CandidateResponse, ErrorResponse
from app.services.storage import InMemoryStorage
from app.services.candidate import CandidateService
from app.utils.file_handler import FileHandler
from app.utils.logger import get_logger
from app.utils.exceptions import (
    CandidateNotFoundError,
    InvalidFileTypeError,
    FileSizeExceededError
)

logger = get_logger(__name__)

router = APIRouter(prefix="/candidates", tags=["Candidates"])

# Dependency injection
storage = InMemoryStorage()
file_handler = FileHandler()


def get_candidate_service() -> CandidateService:
    """Dependency injection for candidate service."""
    return CandidateService(storage=storage, file_handler=file_handler)


@router.post(
    "",
    response_model=CandidateResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Upload Candidate Resume",
    description="""
    Upload a new candidate resume with complete details.
    
    This endpoint accepts multipart/form-data and allows you to:
    - Upload resume files (PDF, DOC, DOCX formats only)
    - Store candidate metadata including personal and professional information
    - Automatically validate all input fields
    - Generate unique candidate ID
    
    **File Requirements:**
    - Formats: PDF, DOC, DOCX
    - Maximum size: 10 MB
    
    **Required Fields:**
    - full_name: Candidate's complete name (2-100 characters)
    - dob: Date of birth in YYYY-MM-DD format (must be past date)
    - contact_number: 10-12 digit phone number (with/without country code)
    - contact_address: Full address (10-500 characters)
    - education_qualification: Highest education (2-100 characters)
    - graduation_year: Year of graduation (1950-2030)
    - years_of_experience: Professional experience in years (0-50)
    - skill_set: Comma-separated list of technical skills
    - resume: Resume file upload
    
    **Validation:**
    - Date of birth must be a valid past date
    - Phone number must be 10-12 digits
    - At least one skill must be provided
    - File type and size are validated
    
    **Returns:**
    - Complete candidate profile with unique ID
    - Stored filename for the resume
    - Timestamp of creation
    """,
    responses={
        201: {
            "description": "Resume uploaded successfully",
            "content": {
                "application/json": {
                    "example": {
                        "id": 1,
                        "full_name": "John Doe",
                        "dob": "1995-06-15",
                        "contact_number": "9876543210",
                        "contact_address": "123 Main Street, City, State, PIN-123456",
                        "education_qualification": "B.Tech in Computer Science",
                        "graduation_year": 2020,
                        "years_of_experience": 3.5,
                        "skill_set": ["Python", "FastAPI", "Docker", "PostgreSQL"],
                        "resume_filename": "abc123def456.pdf",
                        "created_at": "2026-02-15T20:46:55"
                    }
                }
            }
        },
        400: {
            "description": "Validation error or invalid file",
            "model": ErrorResponse
        },
        413: {
            "description": "File size exceeds maximum limit",
            "model": ErrorResponse
        }
    }
)
async def upload_resume(
    full_name: str = Form(..., description="Candidate's full name"),
    dob: str = Form(..., description="Date of birth (YYYY-MM-DD)"),
    contact_number: str = Form(..., description="Contact phone number"),
    contact_address: str = Form(..., description="Full contact address"),
    education_qualification: str = Form(..., description="Highest education qualification"),
    graduation_year: int = Form(..., description="Year of graduation"),
    years_of_experience: float = Form(..., description="Years of professional experience"),
    skill_set: str = Form(..., description="Comma-separated list of skills"),
    resume: UploadFile = File(..., description="Resume file (PDF/DOC/DOCX)"),
    service: CandidateService = Depends(get_candidate_service)
) -> CandidateResponse:
    """
    Upload a new candidate resume with metadata.
    
    Args:
        full_name: Candidate's full name
        dob: Date of birth in YYYY-MM-DD format
        contact_number: Contact phone number
        contact_address: Full address
        education_qualification: Education qualification
        graduation_year: Year of graduation
        years_of_experience: Years of experience
        skill_set: Comma-separated skills
        resume: Resume file upload
        service: Injected candidate service
        
    Returns:
        CandidateResponse: Created candidate with ID
        
    Raises:
        HTTPException: For validation errors or file issues
    """
    try:
        logger.info(f"Resume upload request: {full_name}")
        
        # Parse skill set (comma-separated string to list)
        skills = [skill.strip() for skill in skill_set.split(',') if skill.strip()]
        
        # Create candidate data model
        candidate_data = CandidateCreate(
            full_name=full_name,
            dob=dob,
            contact_number=contact_number,
            contact_address=contact_address,
            education_qualification=education_qualification,
            graduation_year=graduation_year,
            years_of_experience=years_of_experience,
            skill_set=skills
        )
        
        # Create candidate
        result = await service.create_candidate(candidate_data, resume)
        
        logger.info(f"Resume uploaded successfully: ID={result.id}, Name={result.full_name}")
        return result
        
    except InvalidFileTypeError as e:
        logger.warning(f"Invalid file type: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": "InvalidFileType", "message": e.message, "detail": e.detail}
        )
    except FileSizeExceededError as e:
        logger.warning(f"File size exceeded: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail={"error": "FileSizeExceeded", "message": e.message, "detail": e.detail}
        )
    except ValueError as e:
        logger.warning(f"Validation error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": "ValidationError", "message": str(e)}
        )
    except Exception as e:
        logger.error(f"Error uploading resume: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": "InternalServerError", "message": "Failed to upload resume"}
        )


@router.get(
    "",
    response_model=List[CandidateResponse],
    status_code=status.HTTP_200_OK,
    summary="List All Candidates",
    description="""
    Retrieve a list of all candidates with optional filtering.
    
    This endpoint allows you to:
    - Get all candidates in the system
    - Filter by specific skill (case-insensitive partial match)
    - Filter by experience range (minimum and/or maximum years)
    - Filter by graduation year
    - Combine multiple filters for precise results
    
    **Query Parameters (all optional):**
    - `skill`: Filter candidates who have this skill (e.g., "Python", "java")
    - `min_experience`: Minimum years of experience (e.g., 2.0)
    - `max_experience`: Maximum years of experience (e.g., 5.0)
    - `graduation_year`: Filter by specific graduation year (e.g., 2020)
    
    **Filtering Logic:**
    - Skill matching is case-insensitive and partial (e.g., "python" matches "Python", "python3")
    - Experience filters are inclusive (min_experience <= experience <= max_experience)
    - Multiple filters are combined with AND logic
    - No filters returns all candidates
    
    **Examples:**
    - `/candidates` - Get all candidates
    - `/candidates?skill=Python` - Get candidates with Python skill
    - `/candidates?min_experience=2&max_experience=5` - Get candidates with 2-5 years experience
    - `/candidates?graduation_year=2020` - Get 2020 graduates
    - `/candidates?skill=Python&min_experience=3` - Get Python developers with 3+ years experience
    
    **Returns:**
    - Array of candidate profiles matching the filters
    - Empty array if no matches found
    """,
    responses={
        200: {
            "description": "List of candidates retrieved successfully",
            "content": {
                "application/json": {
                    "example": [
                        {
                            "id": 1,
                            "full_name": "John Doe",
                            "dob": "1995-06-15",
                            "contact_number": "9876543210",
                            "contact_address": "123 Main Street, City, State, PIN-123456",
                            "education_qualification": "B.Tech in Computer Science",
                            "graduation_year": 2020,
                            "years_of_experience": 3.5,
                            "skill_set": ["Python", "FastAPI", "Docker"],
                            "resume_filename": "abc123.pdf",
                            "created_at": "2026-02-15T20:46:55"
                        }
                    ]
                }
            }
        },
        400: {
            "description": "Invalid filter parameters",
            "model": ErrorResponse
        }
    }
)
async def list_candidates(
    skill: Optional[str] = None,
    min_experience: Optional[float] = None,
    max_experience: Optional[float] = None,
    graduation_year: Optional[int] = None,
    service: CandidateService = Depends(get_candidate_service)
) -> List[CandidateResponse]:
    """
    List all candidates with optional filters.
    
    Args:
        skill: Filter by skill (optional)
        min_experience: Minimum experience (optional)
        max_experience: Maximum experience (optional)
        graduation_year: Filter by graduation year (optional)
        service: Injected candidate service
        
    Returns:
        List[CandidateResponse]: List of matching candidates
        
    Raises:
        HTTPException: For invalid parameters
    """
    try:
        logger.info(
            f"List candidates request: skill={skill}, min_exp={min_experience}, "
            f"max_exp={max_experience}, grad_year={graduation_year}"
        )
        
        # Validate experience range
        if min_experience is not None and max_experience is not None:
            if max_experience < min_experience:
                raise ValueError("max_experience must be greater than or equal to min_experience")
        
        candidates = service.list_candidates(
            skill=skill,
            min_experience=min_experience,
            max_experience=max_experience,
            graduation_year=graduation_year
        )
        
        logger.info(f"Retrieved {len(candidates)} candidates")
        return candidates
        
    except ValueError as e:
        logger.warning(f"Validation error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": "ValidationError", "message": str(e)}
        )
    except Exception as e:
        logger.error(f"Error listing candidates: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": "InternalServerError", "message": "Failed to retrieve candidates"}
        )


@router.get(
    "/{candidate_id}",
    response_model=CandidateResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Candidate by ID",
    description="""
    Retrieve detailed information about a specific candidate.
    
    This endpoint allows you to:
    - Get complete candidate profile by their unique ID
    - View all stored information including resume filename
    - Access creation timestamp
    
    **Path Parameters:**
    - `candidate_id`: Unique identifier of the candidate (integer)
    
    **Returns:**
    - Complete candidate profile with all details
    - Resume filename for reference
    - Timestamp of when the resume was uploaded
    
    **Error Cases:**
    - Returns 404 if candidate ID doesn't exist
    - Returns 400 if ID format is invalid
    """,
    responses={
        200: {
            "description": "Candidate retrieved successfully",
            "content": {
                "application/json": {
                    "example": {
                        "id": 1,
                        "full_name": "John Doe",
                        "dob": "1995-06-15",
                        "contact_number": "9876543210",
                        "contact_address": "123 Main Street, City, State, PIN-123456",
                        "education_qualification": "B.Tech in Computer Science",
                        "graduation_year": 2020,
                        "years_of_experience": 3.5,
                        "skill_set": ["Python", "FastAPI", "Docker"],
                        "resume_filename": "abc123.pdf",
                        "created_at": "2026-02-15T20:46:55"
                    }
                }
            }
        },
        404: {
            "description": "Candidate not found",
            "model": ErrorResponse,
            "content": {
                "application/json": {
                    "example": {
                        "error": "CandidateNotFound",
                        "message": "Candidate with ID 999 not found",
                        "timestamp": "2026-02-15T20:46:55"
                    }
                }
            }
        }
    }
)
async def get_candidate(
    candidate_id: int,
    service: CandidateService = Depends(get_candidate_service)
) -> CandidateResponse:
    """
    Get a specific candidate by ID.
    
    Args:
        candidate_id: Unique candidate identifier
        service: Injected candidate service
        
    Returns:
        CandidateResponse: Complete candidate details
        
    Raises:
        HTTPException: 404 if candidate not found
    """
    try:
        logger.info(f"Get candidate request: ID={candidate_id}")
        
        candidate = service.get_candidate_by_id(candidate_id)
        
        logger.info(f"Candidate retrieved: ID={candidate_id}, Name={candidate.full_name}")
        return candidate
        
    except CandidateNotFoundError as e:
        logger.warning(f"Candidate not found: ID={candidate_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": "CandidateNotFound", "message": e.message}
        )
    except Exception as e:
        logger.error(f"Error retrieving candidate {candidate_id}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": "InternalServerError", "message": "Failed to retrieve candidate"}
        )


@router.delete(
    "/{candidate_id}",
    status_code=status.HTTP_200_OK,
    summary="Delete Candidate",
    description="""
    Delete a candidate and their associated resume file.
    
    This endpoint allows you to:
    - Remove a candidate from the system by their ID
    - Automatically delete the associated resume file from storage
    - Get confirmation of deletion with candidate details
    
    **Path Parameters:**
    - `candidate_id`: Unique identifier of the candidate to delete (integer)
    
    **Important Notes:**
    - This operation is irreversible
    - Both the candidate record and resume file will be permanently deleted
    - Returns the deleted candidate's basic information for confirmation
    
    **Returns:**
    - Success message with deleted candidate's ID and name
    - Confirmation that both record and file were removed
    
    **Error Cases:**
    - Returns 404 if candidate ID doesn't exist
    - Returns 400 if ID format is invalid
    - If resume file is missing, candidate record is still deleted with a warning
    """,
    responses={
        200: {
            "description": "Candidate deleted successfully",
            "content": {
                "application/json": {
                    "example": {
                        "message": "Candidate 1 deleted successfully",
                        "deleted_candidate": {
                            "id": 1,
                            "full_name": "John Doe"
                        }
                    }
                }
            }
        },
        404: {
            "description": "Candidate not found",
            "model": ErrorResponse,
            "content": {
                "application/json": {
                    "example": {
                        "error": "CandidateNotFound",
                        "message": "Candidate with ID 999 not found",
                        "timestamp": "2026-02-15T20:46:55"
                    }
                }
            }
        }
    }
)
async def delete_candidate(
    candidate_id: int,
    service: CandidateService = Depends(get_candidate_service)
) -> dict:
    """
    Delete a candidate by ID.
    
    Args:
        candidate_id: Unique candidate identifier
        service: Injected candidate service
        
    Returns:
        dict: Deletion confirmation with candidate info
        
    Raises:
        HTTPException: 404 if candidate not found
    """
    try:
        logger.info(f"Delete candidate request: ID={candidate_id}")
        
        result = service.delete_candidate(candidate_id)
        
        logger.info(f"Candidate deleted: ID={candidate_id}, Name={result['deleted_candidate']['full_name']}")
        return result
        
    except CandidateNotFoundError as e:
        logger.warning(f"Candidate not found for deletion: ID={candidate_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": "CandidateNotFound", "message": e.message}
        )
    except Exception as e:
        logger.error(f"Error deleting candidate {candidate_id}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": "InternalServerError", "message": "Failed to delete candidate"}
        )
