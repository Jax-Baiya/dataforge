"""
DataForge - Database Models
SQLAlchemy ORM models for data storage
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Text
from sqlalchemy.sql import func
from .database import Base


class Record(Base):
    """Processed data record model"""
    __tablename__ = "records"

    id = Column(Integer, primary_key=True, index=True)
    
    # Original data fields
    email = Column(String(255), nullable=True)
    date = Column(String(50), nullable=True)
    amount = Column(Float, nullable=True)
    
    # Additional data fields (flexible)
    name = Column(String(255), nullable=True)
    category = Column(String(100), nullable=True)
    status = Column(String(50), nullable=True)
    
    # Validation status
    is_valid = Column(Boolean, default=True)
    validation_errors = Column(Text, nullable=True)
    
    # Metadata
    source_file = Column(String(255), nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())

    def __repr__(self):
        return f"<Record(id={self.id}, email={self.email}, is_valid={self.is_valid})>"


class ProcessingJob(Base):
    """Track processing jobs"""
    __tablename__ = "processing_jobs"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String(255), nullable=False)
    status = Column(String(50), default="pending")  # pending, processing, completed, failed
    total_rows = Column(Integer, default=0)
    valid_rows = Column(Integer, default=0)
    invalid_rows = Column(Integer, default=0)
    error_message = Column(Text, nullable=True)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, server_default=func.now())

    def __repr__(self):
        return f"<ProcessingJob(id={self.id}, filename={self.filename}, status={self.status})>"
