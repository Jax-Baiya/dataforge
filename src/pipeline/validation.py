"""
DataForge - Data Validation Pipeline
Validates and cleans data records
"""

import re
from datetime import datetime
from typing import Tuple, List, Optional
import pandas as pd


class DataValidator:
    """Validates data records against configurable rules"""

    def __init__(self, config: dict = None):
        self.config = config or {}
        self.email_pattern = re.compile(
            r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        )
        self.date_formats = [
            '%Y-%m-%d',
            '%d/%m/%Y',
            '%m/%d/%Y',
            '%d-%m-%Y',
            '%Y/%m/%d',
        ]

    def validate_email(self, email: str) -> Tuple[bool, Optional[str]]:
        """
        Validate email format.
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        if pd.isna(email) or not email:
            return False, "Email is empty"
        
        email = str(email).strip().lower()
        
        if self.email_pattern.match(email):
            return True, None
        return False, f"Invalid email format: {email}"

    def validate_date(self, date_str: str) -> Tuple[bool, Optional[str], Optional[str]]:
        """
        Validate and standardize date format.
        
        Returns:
            Tuple of (is_valid, error_message, standardized_date)
        """
        if pd.isna(date_str) or not date_str:
            return False, "Date is empty", None
        
        date_str = str(date_str).strip()
        
        for fmt in self.date_formats:
            try:
                parsed = datetime.strptime(date_str, fmt)
                standardized = parsed.strftime('%Y-%m-%d')
                return True, None, standardized
            except ValueError:
                continue
        
        return False, f"Unable to parse date: {date_str}", None

    def validate_amount(self, amount) -> Tuple[bool, Optional[str], Optional[float]]:
        """
        Validate monetary amount.
        
        Returns:
            Tuple of (is_valid, error_message, cleaned_amount)
        """
        if pd.isna(amount):
            return False, "Amount is empty", None
        
        try:
            # Handle string amounts with currency symbols
            if isinstance(amount, str):
                amount = amount.replace('$', '').replace(',', '').strip()
            
            cleaned = float(amount)
            
            if cleaned < 0:
                return False, f"Negative amount: {cleaned}", cleaned
            
            return True, None, round(cleaned, 2)
        except (ValueError, TypeError) as e:
            return False, f"Invalid amount: {amount}", None

    def validate_record(self, record: dict) -> Tuple[bool, List[str], dict]:
        """
        Validate a complete record.
        
        Returns:
            Tuple of (is_valid, errors, cleaned_record)
        """
        errors = []
        cleaned = record.copy()
        is_valid = True

        # Validate email if present
        if 'email' in record:
            valid, error = self.validate_email(record['email'])
            if not valid:
                errors.append(error)
                is_valid = False
            else:
                cleaned['email'] = str(record['email']).strip().lower()

        # Validate date if present
        if 'date' in record:
            valid, error, standardized = self.validate_date(record['date'])
            if not valid:
                errors.append(error)
                is_valid = False
            else:
                cleaned['date'] = standardized

        # Validate amount if present
        if 'amount' in record:
            valid, error, cleaned_amount = self.validate_amount(record['amount'])
            if not valid:
                errors.append(error)
                is_valid = False
            else:
                cleaned['amount'] = cleaned_amount

        return is_valid, errors, cleaned


def validate_dataframe(df: pd.DataFrame, config: dict = None) -> pd.DataFrame:
    """
    Validate entire DataFrame and add validation columns.
    
    Args:
        df: Input DataFrame
        config: Validation configuration
        
    Returns:
        DataFrame with validation results
    """
    validator = DataValidator(config)
    
    results = []
    for _, row in df.iterrows():
        record = row.to_dict()
        is_valid, errors, cleaned = validator.validate_record(record)
        
        cleaned['is_valid'] = is_valid
        cleaned['validation_errors'] = '; '.join(errors) if errors else None
        results.append(cleaned)
    
    return pd.DataFrame(results)
