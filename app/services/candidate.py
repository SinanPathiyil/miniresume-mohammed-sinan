"""
Candidate service - Business logic layer.
Handles candidate operations and coordinates between routes and storage.
"""

from typing import List, Optional
from fastapi import UploadFile

from app.models.schemas import CandidateCreate, CandidateResponse
from app.services.storage import InMemoryStorage
from app.utils.file_handler import FileHandler
from app.utils.logger import get_logger
from app.utils.exceptions import CandidateNotFoundError

logger = get_logger(__name__)


class CandidateService:
    """Service layer for candidate operations."""
    
    def __init__(self, storage: InMemoryStorage, file_handler: FileHandler):
        """
        Initialize candidate service.
        
        Args:
            storage: Storage instance for data persistence
            file_handler: File handler for resume uploads
        """
        self.storage = storage
        self.file_handler = file_handler
        logger.info("CandidateService initialized")
    
    async def create_candidate(
        self,
        candidate_data: CandidateCreate,
        resume_file: UploadFile
    ) -> CandidateResponse:
        """
        Create a new candidate with resume upload.
        
        Args:
            candidate_data: Validated candidate data
            resume_file: Resume file upload
            
        Returns:
            CandidateResponse: Created candidate with ID
            
        Raises:
            InvalidFileTypeError: If file type is not allowed
            FileSizeExceededError: If file size exceeds limit
        """
        try:
            # Save resume file
            logger.info(f"Creating candidate: {candidate_data.full_name}")
            resume_filename = await self.file_handler.save_file(resume_file)
            
            # Prepare data for storage
            storage_data = {
                "full_name": candidate_data.full_name,
                "dob": candidate_data.dob,
                "contact_number": candidate_data.contact_number,
                "contact_address": candidate_data.contact_address,
                "education_qualification": candidate_data.education_qualification,
                "graduation_year": candidate_data.graduation_year,
                "years_of_experience": candidate_data.years_of_experience,
                "skill_set": candidate_data.skill_set,
                "resume_filename": resume_filename
            }
            
            # Store candidate
            candidate = self.storage.create(storage_data)
            
            logger.info(f"Candidate created successfully: ID={candidate['id']}, Name={candidate['full_name']}")
            return CandidateResponse(**candidate)
            
        except Exception as e:
            # If storage fails, clean up uploaded file
            if 'resume_filename' in locals():
                self.file_handler.delete_file(resume_filename)
                logger.error(f"Cleaned up file after failed candidate creation: {resume_filename}")
            raise
    
    def get_candidate_by_id(self, candidate_id: int) -> CandidateResponse:
        """
        Retrieve a candidate by ID.
        
        Args:
            candidate_id: ID of the candidate
            
        Returns:
            CandidateResponse: Candidate data
            
        Raises:
            CandidateNotFoundError: If candidate doesn't exist
        """
        logger.debug(f"Fetching candidate: ID={candidate_id}")
        candidate = self.storage.get_by_id(candidate_id)
        return CandidateResponse(**candidate)
    
    def list_candidates(
        self,
        skill: Optional[str] = None,
        min_experience: Optional[float] = None,
        max_experience: Optional[float] = None,
        graduation_year: Optional[int] = None
    ) -> List[CandidateResponse]:
        """
        List all candidates with optional filtering.
        
        Args:
            skill: Filter by skill
            min_experience: Minimum years of experience
            max_experience: Maximum years of experience
            graduation_year: Filter by graduation year
            
        Returns:
            List[CandidateResponse]: List of candidates
        """
        logger.debug(
            f"Listing candidates with filters: skill={skill}, "
            f"min_exp={min_experience}, max_exp={max_experience}, grad_year={graduation_year}"
        )
        
        if any([skill, min_experience is not None, max_experience is not None, graduation_year]):
            candidates = self.storage.filter_candidates(
                skill=skill,
                min_experience=min_experience,
                max_experience=max_experience,
                graduation_year=graduation_year
            )
        else:
            candidates = self.storage.get_all()
        
        return [CandidateResponse(**c) for c in candidates]
    
    def delete_candidate(self, candidate_id: int) -> dict:
        """
        Delete a candidate and associated resume file.
        
        Args:
            candidate_id: ID of the candidate to delete
            
        Returns:
            dict: Deletion confirmation with candidate info
            
        Raises:
            CandidateNotFoundError: If candidate doesn't exist
        """
        logger.info(f"Deleting candidate: ID={candidate_id}")
        
        # Get candidate data before deletion
        candidate = self.storage.delete(candidate_id)
        
        # Delete associated resume file
        resume_filename = candidate.get('resume_filename')
        if resume_filename:
            file_deleted = self.file_handler.delete_file(resume_filename)
            if file_deleted:
                logger.info(f"Resume file deleted: {resume_filename}")
            else:
                logger.warning(f"Resume file not found during deletion: {resume_filename}")
        
        return {
            "message": f"Candidate {candidate_id} deleted successfully",
            "deleted_candidate": {
                "id": candidate['id'],
                "full_name": candidate['full_name']
            }
        }
    
    def get_statistics(self) -> dict:
        """
        Get storage statistics.
        
        Returns:
            dict: Statistics including total count
        """
        return {
            "total_candidates": self.storage.count()
        }
