"""
In-memory storage service for candidate data.
Provides thread-safe CRUD operations with filtering capabilities.
"""

import threading
from typing import Dict, List, Optional
from datetime import datetime

from app.utils.logger import get_logger
from app.utils.exceptions import CandidateNotFoundError, StorageError

logger = get_logger(__name__)


class InMemoryStorage:
    """Thread-safe in-memory storage for candidate data."""
    
    def __init__(self):
        """Initialize storage with empty data and threading lock."""
        self._data: Dict[int, dict] = {}
        self._lock = threading.Lock()
        self._next_id = 1
        logger.info("InMemoryStorage initialized")
    
    def _generate_id(self) -> int:
        """
        Generate unique auto-incrementing ID.
        
        Returns:
            int: Next available ID
        """
        with self._lock:
            current_id = self._next_id
            self._next_id += 1
            return current_id
    
    def create(self, data: dict) -> dict:
        """
        Create a new candidate record.
        
        Args:
            data: Candidate data dictionary
            
        Returns:
            dict: Created candidate with ID and timestamp
            
        Raises:
            StorageError: If creation fails
        """
        try:
            with self._lock:
                candidate_id = self._generate_id()
                candidate = {
                    "id": candidate_id,
                    **data,
                    "created_at": datetime.now()
                }
                self._data[candidate_id] = candidate
                logger.info(f"Candidate created: ID={candidate_id}, Name={data.get('full_name')}")
                return candidate
        except Exception as e:
            logger.error(f"Error creating candidate: {str(e)}", exc_info=True)
            raise StorageError("Failed to create candidate record", str(e))
    
    def get_by_id(self, candidate_id: int) -> dict:
        """
        Retrieve a candidate by ID.
        
        Args:
            candidate_id: ID of the candidate to retrieve
            
        Returns:
            dict: Candidate data
            
        Raises:
            CandidateNotFoundError: If candidate doesn't exist
        """
        with self._lock:
            if candidate_id not in self._data:
                logger.warning(f"Candidate not found: ID={candidate_id}")
                raise CandidateNotFoundError(candidate_id)
            
            logger.debug(f"Candidate retrieved: ID={candidate_id}")
            return self._data[candidate_id].copy()
    
    def get_all(self) -> List[dict]:
        """
        Retrieve all candidates.
        
        Returns:
            List[dict]: List of all candidate records
        """
        with self._lock:
            candidates = [candidate.copy() for candidate in self._data.values()]
            logger.debug(f"Retrieved all candidates: count={len(candidates)}")
            return candidates
    
    def filter_candidates(
        self,
        skill: Optional[str] = None,
        min_experience: Optional[float] = None,
        max_experience: Optional[float] = None,
        graduation_year: Optional[int] = None
    ) -> List[dict]:
        """
        Filter candidates based on criteria.
        
        Args:
            skill: Filter by skill (case-insensitive partial match)
            min_experience: Minimum years of experience
            max_experience: Maximum years of experience
            graduation_year: Filter by graduation year
            
        Returns:
            List[dict]: Filtered list of candidates
        """
        with self._lock:
            candidates = list(self._data.values())
            
            # Apply filters
            if skill:
                skill_lower = skill.lower()
                candidates = [
                    c for c in candidates
                    if any(skill_lower in s.lower() for s in c.get('skill_set', []))
                ]
            
            if min_experience is not None:
                candidates = [
                    c for c in candidates
                    if c.get('years_of_experience', 0) >= min_experience
                ]
            
            if max_experience is not None:
                candidates = [
                    c for c in candidates
                    if c.get('years_of_experience', 0) <= max_experience
                ]
            
            if graduation_year is not None:
                candidates = [
                    c for c in candidates
                    if c.get('graduation_year') == graduation_year
                ]
            
            logger.info(
                f"Filtered candidates: skill={skill}, min_exp={min_experience}, "
                f"max_exp={max_experience}, grad_year={graduation_year}, result_count={len(candidates)}"
            )
            
            return [c.copy() for c in candidates]
    
    def delete(self, candidate_id: int) -> dict:
        """
        Delete a candidate by ID.
        
        Args:
            candidate_id: ID of the candidate to delete
            
        Returns:
            dict: Deleted candidate data
            
        Raises:
            CandidateNotFoundError: If candidate doesn't exist
        """
        with self._lock:
            if candidate_id not in self._data:
                logger.warning(f"Candidate not found for deletion: ID={candidate_id}")
                raise CandidateNotFoundError(candidate_id)
            
            candidate = self._data.pop(candidate_id)
            logger.info(f"Candidate deleted: ID={candidate_id}, Name={candidate.get('full_name')}")
            return candidate
    
    def exists(self, candidate_id: int) -> bool:
        """
        Check if a candidate exists.
        
        Args:
            candidate_id: ID to check
            
        Returns:
            bool: True if candidate exists, False otherwise
        """
        with self._lock:
            return candidate_id in self._data
    
    def count(self) -> int:
        """
        Get total number of candidates.
        
        Returns:
            int: Total count
        """
        with self._lock:
            return len(self._data)
    
    def clear(self) -> None:
        """Clear all data (useful for testing)."""
        with self._lock:
            self._data.clear()
            self._next_id = 1
            logger.warning("Storage cleared - all data removed")
