"""
File handling utilities for resume uploads.
Provides secure file validation, storage, and management.
"""

import os
import uuid
from pathlib import Path
from typing import Optional
from fastapi import UploadFile

from app.config import settings
from app.utils.exceptions import InvalidFileTypeError, FileSizeExceededError
from app.utils.logger import get_logger

logger = get_logger(__name__)


class FileHandler:
    """Handles file upload validation and storage operations."""
    
    def __init__(self):
        """Initialize file handler and create upload directory if needed."""
        self.upload_dir = Path(settings.UPLOAD_DIR)
        self.upload_dir.mkdir(exist_ok=True)
        logger.info(f"FileHandler initialized with upload directory: {self.upload_dir}")
    
    def validate_file_type(self, filename: str) -> bool:
        """
        Validate file extension against allowed types.
        
        Args:
            filename: Name of the file to validate
            
        Returns:
            bool: True if file type is valid
            
        Raises:
            InvalidFileTypeError: If file type is not allowed
        """
        file_ext = Path(filename).suffix.lower()
        
        if file_ext not in settings.ALLOWED_EXTENSIONS:
            logger.warning(f"Invalid file type attempted: {filename} ({file_ext})")
            raise InvalidFileTypeError(filename, settings.ALLOWED_EXTENSIONS)
        
        return True
    
    async def validate_file_size(self, file: UploadFile) -> bool:
        """
        Validate file size against maximum limit.
        
        Args:
            file: Uploaded file to validate
            
        Returns:
            bool: True if file size is valid
            
        Raises:
            FileSizeExceededError: If file size exceeds limit
        """
        # Read file content to check size
        content = await file.read()
        file_size = len(content)
        
        # Reset file pointer for later use
        await file.seek(0)
        
        if file_size > settings.MAX_FILE_SIZE:
            logger.warning(
                f"File size exceeded: {file.filename} "
                f"({file_size / (1024*1024):.2f} MB > {settings.MAX_FILE_SIZE / (1024*1024):.2f} MB)"
            )
            raise FileSizeExceededError(file.filename, file_size, settings.MAX_FILE_SIZE)
        
        logger.debug(f"File size validated: {file.filename} ({file_size / 1024:.2f} KB)")
        return True
    
    def generate_unique_filename(self, original_filename: str) -> str:
        """
        Generate a unique filename using UUID while preserving extension.
        
        Args:
            original_filename: Original name of the uploaded file
            
        Returns:
            str: Unique filename with original extension
        """
        file_ext = Path(original_filename).suffix.lower()
        unique_name = f"{uuid.uuid4().hex}{file_ext}"
        logger.debug(f"Generated unique filename: {original_filename} -> {unique_name}")
        return unique_name
    
    async def save_file(self, file: UploadFile) -> str:
        """
        Save uploaded file to disk with validation.
        
        Args:
            file: File to save
            
        Returns:
            str: Saved filename (unique)
            
        Raises:
            InvalidFileTypeError: If file type is not allowed
            FileSizeExceededError: If file size exceeds limit
        """
        try:
            # Validate file type
            self.validate_file_type(file.filename)
            
            # Validate file size
            await self.validate_file_size(file)
            
            # Generate unique filename
            unique_filename = self.generate_unique_filename(file.filename)
            file_path = self.upload_dir / unique_filename
            
            # Save file
            content = await file.read()
            with open(file_path, 'wb') as f:
                f.write(content)
            
            logger.info(f"File saved successfully: {file.filename} -> {unique_filename} ({len(content) / 1024:.2f} KB)")
            return unique_filename
            
        except (InvalidFileTypeError, FileSizeExceededError):
            raise
        except Exception as e:
            logger.error(f"Error saving file {file.filename}: {str(e)}", exc_info=True)
            raise Exception(f"Failed to save file: {str(e)}")
    
    def delete_file(self, filename: str) -> bool:
        """
        Delete a file from storage.
        
        Args:
            filename: Name of the file to delete
            
        Returns:
            bool: True if file was deleted, False if file didn't exist
        """
        try:
            file_path = self.upload_dir / filename
            
            if file_path.exists():
                file_path.unlink()
                logger.info(f"File deleted successfully: {filename}")
                return True
            else:
                logger.warning(f"File not found for deletion: {filename}")
                return False
                
        except Exception as e:
            logger.error(f"Error deleting file {filename}: {str(e)}", exc_info=True)
            return False
    
    def file_exists(self, filename: str) -> bool:
        """
        Check if a file exists in storage.
        
        Args:
            filename: Name of the file to check
            
        Returns:
            bool: True if file exists, False otherwise
        """
        file_path = self.upload_dir / filename
        return file_path.exists()
    
    def get_file_path(self, filename: str) -> Optional[Path]:
        """
        Get the full path of a stored file.
        
        Args:
            filename: Name of the file
            
        Returns:
            Optional[Path]: Full path if file exists, None otherwise
        """
        file_path = self.upload_dir / filename
        return file_path if file_path.exists() else None
