"""
Date and datetime utility functions for attribution analysis.

Handles date parsing, comparison, and conversion from various formats.
"""

from datetime import datetime, date
from typing import Optional, Union
import pandas as pd


def parse_date(date_value: Union[str, datetime, date], format: Optional[str] = None) -> Optional[date]:
    """
    Parse various date formats into a date object.
    
    Supports:
    - ISO format: "2024-01-15" or "2024-01-15T10:30:00"
    - US format: "01/15/2024"
    - Custom formats via format parameter
    
    Args:
        date_value: Date string or datetime object to parse
        format: Optional strptime format string
        
    Returns:
        date object, or None if parsing fails
        
    Example:
        >>> parse_date("2024-01-15")
        datetime.date(2024, 1, 15)
        >>> parse_date("01/15/2024", "%m/%d/%Y")
        datetime.date(2024, 1, 15)
    """
    if date_value is None or date_value == '':
        return None
    
    # Already a date object
    if isinstance(date_value, date):
        return date_value
    
    # Already a datetime object
    if isinstance(date_value, datetime):
        return date_value.date()
    
    # Convert to string
    date_str = str(date_value)
    
    # Try to extract just the date part if it contains time
    if 'T' in date_str:
        date_str = date_str.split('T')[0]
    elif ' ' in date_str:
        date_str = date_str.split(' ')[0]
    
    # List of common formats to try
    formats_to_try = [
        "%Y-%m-%d",       # ISO format
        "%m/%d/%Y",       # US format
        "%d/%m/%Y",       # European format
        "%Y/%m/%d",       # Alternative ISO
        "%m-%d-%Y",       # US with dashes
        "%d-%m-%Y",       # European with dashes
    ]
    
    # Add custom format to beginning of list if provided
    if format:
        formats_to_try.insert(0, format)
    
    # Try each format
    for fmt in formats_to_try:
        try:
            return datetime.strptime(date_str, fmt).date()
        except (ValueError, TypeError):
            continue
    
    return None


def parse_datetime(datetime_value: Union[str, datetime], format: Optional[str] = None) -> Optional[datetime]:
    """
    Parse various datetime formats into a datetime object.
    
    Args:
        datetime_value: Datetime string or object to parse
        format: Optional strptime format string
        
    Returns:
        datetime object, or None if parsing fails
        
    Example:
        >>> parse_datetime("2024-01-15T10:30:00")
        datetime.datetime(2024, 1, 15, 10, 30)
    """
    if datetime_value is None or datetime_value == '':
        return None
    
    # Already a datetime object
    if isinstance(datetime_value, datetime):
        return datetime_value
    
    datetime_str = str(datetime_value)
    
    # List of common formats to try
    formats_to_try = [
        "%Y-%m-%dT%H:%M:%S",         # ISO with T
        "%Y-%m-%d %H:%M:%S",         # ISO with space
        "%m/%d/%Y %H:%M:%S",         # US format
        "%Y-%m-%d %H:%M:%S.%f",      # ISO with microseconds
    ]
    
    if format:
        formats_to_try.insert(0, format)
    
    for fmt in formats_to_try:
        try:
            return datetime.strptime(datetime_str, fmt)
        except (ValueError, TypeError):
            continue
    
    return None


def date_to_string(date_value: Union[date, datetime], format: str = "%Y-%m-%d") -> str:
    """
    Convert a date or datetime to string.
    
    Args:
        date_value: date or datetime object
        format: strftime format string (default: ISO format)
        
    Returns:
        Formatted date string
        
    Example:
        >>> date_to_string(datetime.date(2024, 1, 15))
        '2024-01-15'
    """
    if isinstance(date_value, datetime):
        return date_value.strftime(format)
    elif isinstance(date_value, date):
        return date_value.strftime(format)
    return str(date_value)


def is_before(date1: Union[str, date, datetime], 
              date2: Union[str, date, datetime]) -> bool:
    """
    Check if date1 is before date2.
    
    Args:
        date1: First date (any parseable format)
        date2: Second date (any parseable format)
        
    Returns:
        True if date1 < date2, False otherwise
        
    Example:
        >>> is_before("2024-01-15", "2024-01-20")
        True
    """
    parsed1 = parse_date(date1)
    parsed2 = parse_date(date2)
    
    if parsed1 is None or parsed2 is None:
        return False
    
    return parsed1 < parsed2


def is_after(date1: Union[str, date, datetime], 
             date2: Union[str, date, datetime]) -> bool:
    """
    Check if date1 is after date2.
    
    Args:
        date1: First date (any parseable format)
        date2: Second date (any parseable format)
        
    Returns:
        True if date1 > date2, False otherwise
    """
    parsed1 = parse_date(date1)
    parsed2 = parse_date(date2)
    
    if parsed1 is None or parsed2 is None:
        return False
    
    return parsed1 > parsed2


def is_same_day(date1: Union[str, date, datetime], 
                date2: Union[str, date, datetime]) -> bool:
    """
    Check if two dates are the same day.
    
    Args:
        date1: First date (any parseable format)
        date2: Second date (any parseable format)
        
    Returns:
        True if same day, False otherwise
    """
    parsed1 = parse_date(date1)
    parsed2 = parse_date(date2)
    
    if parsed1 is None or parsed2 is None:
        return False
    
    return parsed1 == parsed2


def days_between(date1: Union[str, date, datetime], 
                 date2: Union[str, date, datetime]) -> Optional[int]:
    """
    Calculate number of days between two dates.
    
    Args:
        date1: First date (any parseable format)
        date2: Second date (any parseable format)
        
    Returns:
        Number of days (positive if date2 > date1), or None if parsing fails
        
    Example:
        >>> days_between("2024-01-15", "2024-01-20")
        5
    """
    parsed1 = parse_date(date1)
    parsed2 = parse_date(date2)
    
    if parsed1 is None or parsed2 is None:
        return None
    
    return (parsed2 - parsed1).days


def parse_date_column(series: pd.Series, format: Optional[str] = None) -> pd.Series:
    """
    Parse a pandas Series of dates.
    
    Args:
        series: Pandas Series containing date strings
        format: Optional strptime format
        
    Returns:
        Series with parsed date objects
    """
    return series.apply(lambda x: parse_date(x, format))


def extract_date_from_datetime(series: pd.Series) -> pd.Series:
    """
    Extract date component from datetime strings or objects.
    
    Args:
        series: Pandas Series containing datetime values
        
    Returns:
        Series with date objects
    """
    def extract_date(value):
        if pd.isna(value):
            return None
        if isinstance(value, date):
            return value
        if isinstance(value, datetime):
            return value.date()
        parsed = parse_datetime(value)
        return parsed.date() if parsed else None
    
    return series.apply(extract_date)
