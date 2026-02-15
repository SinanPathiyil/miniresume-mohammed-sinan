"""
Pydantic schemas for request/response validation.
Provides comprehensive validation rules for all API endpoints.
"""

from typing import List, Optional
from datetime import datetime, date
from pydantic import BaseModel, Field, field_validator, ConfigDict
import re


class CandidateCreate(BaseModel):
    """Schema for creating a new candidate resume."""
    
    full_name: str = Field(
        ..., 
        min_length=2, 
        max_length=100,
        description="Candidate's full name",
        examples=["John Doe"]
    )
    dob: str = Field(
        ..., 
        description="Date of birth in YYYY-MM-DD format",
        examples=["1995-06-15"]
    )
    contact_number: str = Field(
        ..., 
        description="Contact phone number (10 digits or with country code)",
        examples=["+919876543210", "9876543210"]
    )
    contact_address: str = Field(
        ..., 
        min_length=10,
        max_length=500,
        description="Full contact address",
        examples=["123 Main Street, City, State, PIN-123456"]
    )
    education_qualification: str = Field(
        ..., 
        min_length=2,
        max_length=100,
        description="Highest education qualification",
        examples=["B.Tech in Computer Science", "M.Sc in Data Science"]
    )
    graduation_year: int = Field(
        ..., 
        ge=1950, 
        le=2030,
        description="Year of graduation",
        examples=[2020]
    )
    years_of_experience: float = Field(
        ..., 
        ge=0, 
        le=50,
        description="Total years of professional experience",
        examples=[3.5]
    )
    skill_set: List[str] = Field(
        ..., 
        min_length=1,
        description="List of technical skills",
        examples=[["Python", "FastAPI", "Docker", "PostgreSQL"]]
    )
    
    @field_validator('dob')
    @classmethod
    def validate_dob(cls, v: str) -> str:
        """Validate date of birth format and ensure it's a past date."""
        try:
            dob_date = datetime.strptime(v, '%Y-%m-%d').date()
            if dob_date >= date.today():
                raise ValueError('Date of birth must be in the past')
            if dob_date.year < 1900:
                raise ValueError('Date of birth year must be after 1900')
            return v
        except ValueError as e:
            if 'does not match format' in str(e):
                raise ValueError('Date of birth must be in YYYY-MM-DD format')
            raise e
    
    @field_validator('contact_number')
    @classmethod
    def validate_contact_number(cls, v: str) -> str:
        """Validate contact number format."""
        # Remove spaces and dashes
        cleaned = re.sub(r'[\s\-]', '', v)
        
        # Check if it matches valid phone number patterns
        if not re.match(r'^(\+\d{1,3})?\d{10,12}$', cleaned):
            raise ValueError(
                'Contact number must be 10-12 digits, optionally with country code (e.g., +919876543210 or 9876543210)'
            )
        return cleaned
    
    @field_validator('skill_set')
    @classmethod
    def validate_skill_set(cls, v: List[str]) -> List[str]:
        """Validate and clean skill set."""
        if not v:
            raise ValueError('At least one skill must be provided')
        
        # Remove empty strings and duplicates (case-insensitive)
        cleaned = []
        seen = set()
        for skill in v:
            skill_clean = skill.strip()
            if skill_clean and skill_clean.lower() not in seen:
                cleaned.append(skill_clean)
                seen.add(skill_clean.lower())
        
        if not cleaned:
            raise ValueError('At least one valid skill must be provided')
        
        return cleaned

    model_config = ConfigDict(str_strip_whitespace=True)


class CandidateResponse(BaseModel):
    """Schema for candidate response."""
    
    id: int = Field(..., description="Unique candidate ID")
    full_name: str = Field(..., description="Candidate's full name")
    dob: str = Field(..., description="Date of birth")
    contact_number: str = Field(..., description="Contact phone number")
    contact_address: str = Field(..., description="Contact address")
    education_qualification: str = Field(..., description="Education qualification")
    graduation_year: int = Field(..., description="Graduation year")
    years_of_experience: float = Field(..., description="Years of experience")
    skill_set: List[str] = Field(..., description="List of skills")
    resume_filename: str = Field(..., description="Stored resume filename")
    created_at: datetime = Field(..., description="Timestamp when resume was uploaded")
    
    model_config = ConfigDict(from_attributes=True)


class CandidateFilter(BaseModel):
    """Schema for filtering candidates."""
    
    skill: Optional[str] = Field(
        None, 
        description="Filter by specific skill (case-insensitive partial match)",
        examples=["Python"]
    )
    min_experience: Optional[float] = Field(
        None, 
        ge=0,
        description="Minimum years of experience",
        examples=[2.0]
    )
    max_experience: Optional[float] = Field(
        None, 
        ge=0,
        description="Maximum years of experience",
        examples=[5.0]
    )
    graduation_year: Optional[int] = Field(
        None, 
        ge=1950, 
        le=2030,
        description="Filter by graduation year",
        examples=[2020]
    )
    
    @field_validator('max_experience')
    @classmethod
    def validate_experience_range(cls, v: Optional[float], info) -> Optional[float]:
        """Ensure max_experience is greater than min_experience."""
        if v is not None and info.data.get('min_experience') is not None:
            if v < info.data['min_experience']:
                raise ValueError('max_experience must be greater than or equal to min_experience')
        return v


class HealthResponse(BaseModel):
    """Schema for health check response."""
    
    status: str = Field(..., description="Application status", examples=["healthy"])
    timestamp: datetime = Field(..., description="Current timestamp")
    version: str = Field(..., description="Application version", examples=["1.0.0"])
    message: str = Field(..., description="Status message", examples=["Service is running"])


class ErrorResponse(BaseModel):
    """Schema for error responses."""
    
    error: str = Field(..., description="Error type", examples=["ValidationError"])
    message: str = Field(..., description="Error message", examples=["Invalid input provided"])
    detail: Optional[str] = Field(None, description="Detailed error information")
    timestamp: datetime = Field(..., description="Error timestamp")
