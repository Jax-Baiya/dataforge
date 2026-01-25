"""
DataForge - FastAPI Application
Main entry point for the REST API
"""

from fastapi import FastAPI, UploadFile, File, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List, Optional
import tempfile
import os

from .db.database import get_db, init_db
from .db.models import Record, ProcessingJob
from .api.schemas import RecordResponse, RecordCreate, StatsResponse, JobResponse
from .api.routes import router as api_router

# Create FastAPI app
app = FastAPI(
    title="DataForge API",
    description="Data processing pipeline with REST API",
    version="1.0.0",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(api_router, prefix="/api")


@app.on_event("startup")
async def startup():
    """Initialize database on startup"""
    init_db()


@app.get("/")
async def root():
    """Root endpoint - API info"""
    return {
        "name": "DataForge API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health",
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "dataforge"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
