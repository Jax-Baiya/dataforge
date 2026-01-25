"""
DataForge - API Schemas
Pydantic models for API request/response validation
"""

from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime


class RecordBase(BaseModel):
    """Base record schema"""
    email: Optional[str] = None
    date: Optional[str] = None
    amount: Optional[float] = None
    name: Optional[str] = None
    category: Optional[str] = None
    status: Optional[str] = None


class RecordCreate(RecordBase):
    """Schema for creating a record"""
    pass


class RecordResponse(RecordBase):
    """Schema for record response"""
    id: int
    is_valid: bool
    validation_errors: Optional[str] = None
    source_file: Optional[str] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class RecordListResponse(BaseModel):
    """Schema for paginated record list"""
    records: List[RecordResponse]
    total: int
    page: int
    page_size: int


class JobResponse(BaseModel):
    """Schema for processing job response"""
    id: int
    filename: str
    status: str
    total_rows: int
    valid_rows: int
    invalid_rows: int
    error_message: Optional[str] = None
    created_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class StatsResponse(BaseModel):
    """Schema for statistics response"""
    total_records: int
    valid_records: int
    invalid_records: int
    total_jobs: int
    completed_jobs: int
    failed_jobs: int


class UploadResponse(BaseModel):
    """Schema for file upload response"""
    message: str
    job_id: int
    filename: str
    rows_processed: int
    valid_rows: int
    invalid_rows: int
