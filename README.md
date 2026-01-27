# DataForge

> A unified data processing pipeline with REST API and CLI interface

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green.svg)](https://fastapi.tiangolo.com)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## Overview

DataForge is a modular data processing system that combines:
- **Data Pipeline**: Clean, validate, and transform CSV data
- **REST API**: Query and manage processed data via HTTP
- **CLI Tool**: Local operations and automation

Built to demonstrate real-world backend and data engineering patterns.

---

## Features

- ✅ **Data Ingestion** — Upload CSV files for processing
- ✅ **Validation Pipeline** — Email, date, and amount validation
- ✅ **Database Storage** — SQLite persistence layer
- ✅ **REST API** — FastAPI endpoints for data access
- ✅ **CLI Interface** — Command-line operations
- ✅ **Config-driven** — YAML configuration for flexibility

---

## Project Structure

```
dataforge/
├── src/
│   ├── __init__.py
│   ├── main.py           # FastAPI application entry
│   ├── pipeline/         # Data processing pipeline
│   │   ├── __init__.py
│   │   ├── ingestion.py  # File loading
│   │   ├── validation.py # Data validation
│   │   └── transform.py  # Data transformation
│   ├── api/              # REST API layer
│   │   ├── __init__.py
│   │   ├── routes.py     # API endpoints
│   │   └── schemas.py    # Pydantic models
│   ├── db/               # Database layer
│   │   ├── __init__.py
│   │   ├── models.py     # SQLAlchemy models
│   │   └── database.py   # DB connection
│   └── cli/              # CLI interface
│       ├── __init__.py
│       └── commands.py   # CLI commands
├── tests/
│   ├── test_pipeline.py
│   ├── test_api.py
│   └── test_cli.py
├── data/
│   ├── input/            # Raw CSV files
│   └── output/           # Processed files
├── config/
│   └── config.yaml       # Application config
├── docs/
│   └── API.md            # API documentation
├── requirements.txt
├── README.md
└── .gitignore
```

---

## Quick Start

### 1. Setup

```bash
git clone https://github.com/Jax-Baiya/dataforge.git
cd dataforge
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
```

### 2. Process Data (CLI)

```bash
# Ingest and process a CSV file
python -m src.cli.commands ingest data/input/sample.csv

# View processing status
python -m src.cli.commands status
```

### 3. Start API Server

```bash
uvicorn src.main:app --reload
```

### 4. Query Data (API)

```bash
# Get all records
curl http://localhost:8000/api/records

# Get record by ID
curl http://localhost:8000/api/records/1

# Upload new file
curl -X POST -F "file=@data.csv" http://localhost:8000/api/upload
```

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/records` | List all records |
| GET | `/api/records/{id}` | Get record by ID |
| POST | `/api/upload` | Upload CSV for processing |
| GET | `/api/stats` | Processing statistics |
| GET | `/health` | Health check |

---

## Tech Stack

- **Python 3.9+** — Core language
- **FastAPI** — REST API framework
- **SQLite** — Database storage
- **SQLAlchemy** — ORM
- **Pandas** — Data processing
- **Typer** — CLI framework
- **Pydantic** — Data validation

---

## Configuration

Edit `config/config.yaml`:

```yaml
database:
  url: "sqlite:///data/dataforge.db"

pipeline:
  validate_emails: true
  date_format: "%Y-%m-%d"
  
api:
  host: "0.0.0.0"
  port: 8000
```

---

## Development

```bash
# Run tests
pytest tests/

# Format code
black src/

# Type checking
mypy src/
```

---

## Author

**Jax Baiya**  
Backend Developer | Data Engineer

🔗 [GitHub](https://github.com/Jax-Baiya) | [LinkedIn](https://linkedin.com/in/jackline-baiya-3160a8271)
