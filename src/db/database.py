"""
DataForge - Database Layer
SQLAlchemy database connection and session management
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from pathlib import Path
import yaml

# Load config
config_path = Path(__file__).parent.parent.parent / "config" / "config.yaml"
with open(config_path) as f:
    config = yaml.safe_load(f)

DATABASE_URL = config["database"]["url"]

# Create engine
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}  # SQLite specific
)

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()


def get_db():
    """Dependency for FastAPI - yields database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Initialize database tables"""
    from . import models  # Import models to register them
    Base.metadata.create_all(bind=engine)
