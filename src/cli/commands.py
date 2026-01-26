"""
DataForge - CLI Commands
Command-line interface for local operations
"""

import typer
from pathlib import Path
from typing import Optional
from rich.console import Console
from rich.table import Table
import sys

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.pipeline.ingestion import ingest_file
from src.pipeline.validation import validate_dataframe
from src.db.database import SessionLocal, init_db
from src.db.models import Record, ProcessingJob

app = typer.Typer(help="DataForge CLI - Data processing pipeline")
console = Console()


@app.command()
def ingest(
    filepath: str = typer.Argument(..., help="Path to CSV file"),
    preview: bool = typer.Option(False, "--preview", "-p", help="Preview only, don't save"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Verbose output")
):
    """Ingest and process a CSV file"""
    path = Path(filepath)
    
    if not path.exists():
        console.print(f"[red]Error: File not found: {filepath}[/red]")
        raise typer.Exit(1)
    
    console.print(f"\n[bold blue]📂 Loading:[/bold blue] {path.name}")
    
    try:
        # Load and validate
        df, metadata, column_info = ingest_file(filepath)
        
        console.print(f"[green]✓[/green] Loaded {metadata['row_count']} rows, {metadata['column_count']} columns")
        
        if verbose:
            console.print("\n[bold]Column Info:[/bold]")
            for col, info in column_info.items():
                console.print(f"  • {col}: {info['dtype']} ({info['null_percentage']}% null)")
        
        # Validate
        console.print("\n[bold blue]🔍 Validating...[/bold blue]")
        validated_df = validate_dataframe(df)
        
        valid_count = validated_df['is_valid'].sum()
        invalid_count = len(validated_df) - valid_count
        
        console.print(f"[green]✓[/green] Valid: {valid_count}")
        console.print(f"[yellow]⚠[/yellow] Invalid: {invalid_count}")
        
        if preview:
            console.print("\n[bold]Preview (first 5 rows):[/bold]")
            console.print(validated_df.head().to_string())
            return
        
        # Save to database
        console.print("\n[bold blue]💾 Saving to database...[/bold blue]")
        init_db()
        
        db = SessionLocal()
        try:
            job = ProcessingJob(
                filename=path.name,
                status="completed",
                total_rows=len(validated_df),
                valid_rows=int(valid_count),
                invalid_rows=int(invalid_count)
            )
            db.add(job)
            
            for _, row in validated_df.iterrows():
                record = Record(
                    email=row.get('email'),
                    date=row.get('date'),
                    amount=row.get('amount'),
                    is_valid=row.get('is_valid', True),
                    validation_errors=row.get('validation_errors'),
                    source_file=path.name
                )
                db.add(record)
            
            db.commit()
            console.print(f"[green]✓[/green] Saved {len(validated_df)} records (Job ID: {job.id})")
        finally:
            db.close()
        
        console.print("\n[bold green]✅ Processing complete![/bold green]")
        
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)


@app.command()
def status():
    """Show processing statistics"""
    init_db()
    db = SessionLocal()
    
    try:
        total_records = db.query(Record).count()
        valid_records = db.query(Record).filter(Record.is_valid == True).count()
        total_jobs = db.query(ProcessingJob).count()
        
        table = Table(title="DataForge Status")
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="green")
        
        table.add_row("Total Records", str(total_records))
        table.add_row("Valid Records", str(valid_records))
        table.add_row("Invalid Records", str(total_records - valid_records))
        table.add_row("Processing Jobs", str(total_jobs))
        
        console.print(table)
        
    finally:
        db.close()


@app.command()
def jobs():
    """List all processing jobs"""
    init_db()
    db = SessionLocal()
    
    try:
        all_jobs = db.query(ProcessingJob).order_by(ProcessingJob.id.desc()).limit(10).all()
        
        if not all_jobs:
            console.print("[yellow]No jobs found[/yellow]")
            return
        
        table = Table(title="Recent Processing Jobs")
        table.add_column("ID", style="cyan")
        table.add_column("Filename", style="white")
        table.add_column("Status", style="green")
        table.add_column("Rows", style="white")
        table.add_column("Valid", style="green")
        table.add_column("Invalid", style="red")
        
        for job in all_jobs:
            status_style = "green" if job.status == "completed" else "red"
            table.add_row(
                str(job.id),
                job.filename,
                f"[{status_style}]{job.status}[/{status_style}]",
                str(job.total_rows),
                str(job.valid_rows),
                str(job.invalid_rows)
            )
        
        console.print(table)
        
    finally:
        db.close()


@app.command()
def init():
    """Initialize the database"""
    console.print("[bold blue]Initializing database...[/bold blue]")
    init_db()
    console.print("[green]✓ Database initialized[/green]")


@app.command()
def serve(
    host: str = typer.Option("0.0.0.0", help="Host address"),
    port: int = typer.Option(8000, help="Port number"),
    reload: bool = typer.Option(True, help="Enable auto-reload")
):
    """Start the API server"""
    import uvicorn
    console.print(f"[bold blue]Starting server at http://{host}:{port}[/bold blue]")
    uvicorn.run("src.main:app", host=host, port=port, reload=reload)


if __name__ == "__main__":
    app()
