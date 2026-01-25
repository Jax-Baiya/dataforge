"""
DataForge - API Routes
REST API endpoints for data operations
"""

from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
import tempfile
import os
from datetime import datetime

from ..db.database import get_db
from ..db.models import Record, ProcessingJob
from ..pipeline.ingestion import ingest_file
from ..pipeline.validation import validate_dataframe
from .schemas import (
    RecordResponse, RecordCreate, RecordListResponse,
    StatsResponse, JobResponse, UploadResponse
)

router = APIRouter()


@router.get("/records", response_model=RecordListResponse)
async def list_records(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    valid_only: bool = False,
    db: Session = Depends(get_db)
):
    """List all records with pagination"""
    query = db.query(Record)
    
    if valid_only:
        query = query.filter(Record.is_valid == True)
    
    total = query.count()
    records = query.offset((page - 1) * page_size).limit(page_size).all()
    
    return RecordListResponse(
        records=records,
        total=total,
        page=page,
        page_size=page_size
    )


@router.get("/records/{record_id}", response_model=RecordResponse)
async def get_record(record_id: int, db: Session = Depends(get_db)):
    """Get a single record by ID"""
    record = db.query(Record).filter(Record.id == record_id).first()
    
    if not record:
        raise HTTPException(status_code=404, detail="Record not found")
    
    return record


@router.post("/records", response_model=RecordResponse)
async def create_record(record: RecordCreate, db: Session = Depends(get_db)):
    """Create a new record"""
    db_record = Record(**record.model_dump())
    db.add(db_record)
    db.commit()
    db.refresh(db_record)
    return db_record


@router.delete("/records/{record_id}")
async def delete_record(record_id: int, db: Session = Depends(get_db)):
    """Delete a record"""
    record = db.query(Record).filter(Record.id == record_id).first()
    
    if not record:
        raise HTTPException(status_code=404, detail="Record not found")
    
    db.delete(record)
    db.commit()
    return {"message": f"Record {record_id} deleted"}


@router.post("/upload", response_model=UploadResponse)
async def upload_file(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """Upload and process a CSV file"""
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="Only CSV files are supported")
    
    # Create processing job
    job = ProcessingJob(
        filename=file.filename,
        status="processing",
        started_at=datetime.now()
    )
    db.add(job)
    db.commit()
    
    try:
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix='.csv') as tmp:
            content = await file.read()
            tmp.write(content)
            tmp_path = tmp.name
        
        # Ingest and validate
        df, metadata, _ = ingest_file(tmp_path)
        validated_df = validate_dataframe(df)
        
        # Store records
        valid_count = 0
        invalid_count = 0
        
        for _, row in validated_df.iterrows():
            record = Record(
                email=row.get('email'),
                date=row.get('date'),
                amount=row.get('amount'),
                name=row.get('name'),
                category=row.get('category'),
                status=row.get('status'),
                is_valid=row.get('is_valid', True),
                validation_errors=row.get('validation_errors'),
                source_file=file.filename
            )
            db.add(record)
            
            if row.get('is_valid', True):
                valid_count += 1
            else:
                invalid_count += 1
        
        # Update job
        job.status = "completed"
        job.total_rows = len(validated_df)
        job.valid_rows = valid_count
        job.invalid_rows = invalid_count
        job.completed_at = datetime.now()
        
        db.commit()
        
        # Cleanup
        os.unlink(tmp_path)
        
        return UploadResponse(
            message="File processed successfully",
            job_id=job.id,
            filename=file.filename,
            rows_processed=len(validated_df),
            valid_rows=valid_count,
            invalid_rows=invalid_count
        )
        
    except Exception as e:
        job.status = "failed"
        job.error_message = str(e)
        job.completed_at = datetime.now()
        db.commit()
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats", response_model=StatsResponse)
async def get_stats(db: Session = Depends(get_db)):
    """Get processing statistics"""
    total_records = db.query(Record).count()
    valid_records = db.query(Record).filter(Record.is_valid == True).count()
    invalid_records = total_records - valid_records
    
    total_jobs = db.query(ProcessingJob).count()
    completed_jobs = db.query(ProcessingJob).filter(
        ProcessingJob.status == "completed"
    ).count()
    failed_jobs = db.query(ProcessingJob).filter(
        ProcessingJob.status == "failed"
    ).count()
    
    return StatsResponse(
        total_records=total_records,
        valid_records=valid_records,
        invalid_records=invalid_records,
        total_jobs=total_jobs,
        completed_jobs=completed_jobs,
        failed_jobs=failed_jobs
    )


@router.get("/jobs", response_model=List[JobResponse])
async def list_jobs(db: Session = Depends(get_db)):
    """List all processing jobs"""
    jobs = db.query(ProcessingJob).order_by(ProcessingJob.created_at.desc()).all()
    return jobs


@router.get("/jobs/{job_id}", response_model=JobResponse)
async def get_job(job_id: int, db: Session = Depends(get_db)):
    """Get a processing job by ID"""
    job = db.query(ProcessingJob).filter(ProcessingJob.id == job_id).first()
    
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    return job
