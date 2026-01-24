"""
DataForge - Data Ingestion Pipeline
Handles loading and initial processing of CSV files
"""

import pandas as pd
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime


class DataIngester:
    """Handles CSV file ingestion and initial loading"""

    def __init__(self, config: dict = None):
        self.config = config or {}
        self.supported_extensions = ['.csv', '.CSV']

    def load_csv(self, filepath: str, **kwargs) -> pd.DataFrame:
        """
        Load a CSV file into a DataFrame.
        
        Args:
            filepath: Path to the CSV file
            **kwargs: Additional pandas read_csv arguments
            
        Returns:
            Loaded DataFrame
            
        Raises:
            FileNotFoundError: If file doesn't exist
            ValueError: If file format is not supported
        """
        path = Path(filepath)
        
        if not path.exists():
            raise FileNotFoundError(f"File not found: {filepath}")
        
        if path.suffix not in self.supported_extensions:
            raise ValueError(f"Unsupported file format: {path.suffix}")
        
        # Default read options
        read_options = {
            'encoding': 'utf-8',
            'na_values': ['', 'NA', 'N/A', 'null', 'NULL', 'None'],
        }
        read_options.update(kwargs)
        
        try:
            df = pd.read_csv(filepath, **read_options)
            return df
        except UnicodeDecodeError:
            # Try alternative encoding
            read_options['encoding'] = 'latin-1'
            return pd.read_csv(filepath, **read_options)

    def get_file_metadata(self, filepath: str) -> Dict[str, Any]:
        """
        Extract metadata from a file.
        
        Args:
            filepath: Path to the file
            
        Returns:
            Dictionary with file metadata
        """
        path = Path(filepath)
        stat = path.stat()
        
        return {
            'filename': path.name,
            'size_bytes': stat.st_size,
            'modified_at': datetime.fromtimestamp(stat.st_mtime),
            'extension': path.suffix,
        }

    def preview(self, filepath: str, n_rows: int = 5) -> pd.DataFrame:
        """
        Preview first n rows of a file.
        
        Args:
            filepath: Path to the CSV file
            n_rows: Number of rows to preview
            
        Returns:
            DataFrame with first n rows
        """
        return self.load_csv(filepath, nrows=n_rows)

    def get_column_info(self, df: pd.DataFrame) -> Dict[str, Dict]:
        """
        Get information about DataFrame columns.
        
        Args:
            df: Input DataFrame
            
        Returns:
            Dictionary with column information
        """
        info = {}
        for col in df.columns:
            info[col] = {
                'dtype': str(df[col].dtype),
                'null_count': int(df[col].isna().sum()),
                'null_percentage': round(df[col].isna().mean() * 100, 2),
                'unique_count': int(df[col].nunique()),
                'sample_values': df[col].dropna().head(3).tolist(),
            }
        return info


def ingest_file(filepath: str, config: dict = None) -> tuple:
    """
    Convenience function to ingest a file.
    
    Args:
        filepath: Path to CSV file
        config: Optional configuration
        
    Returns:
        Tuple of (DataFrame, metadata, column_info)
    """
    ingester = DataIngester(config)
    
    df = ingester.load_csv(filepath)
    metadata = ingester.get_file_metadata(filepath)
    column_info = ingester.get_column_info(df)
    
    metadata['row_count'] = len(df)
    metadata['column_count'] = len(df.columns)
    
    return df, metadata, column_info
