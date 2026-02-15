"""
Custom exception classes for the application.
Provides specific exceptions for different error scenarios.
"""

from typing import Optional


class ApplicationError(Exception):
    """Base exception for all application errors."""
    
    def __init__(self, message: str, detail: Optional[str] = None):
        """
        Initialize application error.
        
        Args:
            message: Error message
            detail: Optional detailed error information
        """
        self.message = message
        self.detail = detail
        super().__init__(self.message)


class CandidateNotFoundError(ApplicationError):
    """Raised when a candidate is not found by ID."""
    
    def __init__(self, candidate_id: int):
        """
        Initialize candidate not found error.
        
        Args:
            candidate_id: ID of the candidate that was not found
        """
        message = f"Candidate with ID {candidate_id} not found"
        super().__init__(message)
        self.candidate_id = candidate_id


class InvalidFileTypeError(ApplicationError):
    """Raised when an uploaded file has an invalid type."""
    
    def __init__(self, filename: str, allowed_types: list):
        """
        Initialize invalid file type error.
        
        Args:
            filename: Name of the invalid file
            allowed_types: List of allowed file extensions
        """
        message = f"Invalid file type for '{filename}'"
        detail = f"Allowed types: {', '.join(allowed_types)}"
        super().__init__(message, detail)
        self.filename = filename
        self.allowed_types = allowed_types


class FileSizeExceededError(ApplicationError):
    """Raised when an uploaded file exceeds the maximum size limit."""
    
    def __init__(self, filename: str, file_size: int, max_size: int):
        """
        Initialize file size exceeded error.
        
        Args:
            filename: Name of the file
            file_size: Actual file size in bytes
            max_size: Maximum allowed file size in bytes
        """
        message = f"File '{filename}' size exceeds the maximum limit"
        detail = f"File size: {file_size / (1024*1024):.2f} MB, Max allowed: {max_size / (1024*1024):.2f} MB"
        super().__init__(message, detail)
        self.filename = filename
        self.file_size = file_size
        self.max_size = max_size


class StorageError(ApplicationError):
    """Raised when there's an error with storage operations."""
    
    def __init__(self, message: str, detail: Optional[str] = None):
        """
        Initialize storage error.
        
        Args:
            message: Error message
            detail: Optional detailed error information
        """
        super().__init__(message, detail)
