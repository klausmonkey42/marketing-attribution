"""
Unit tests for utility functions.
"""

import pytest
import sys
from pathlib import Path
from datetime import date, datetime

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from utils.phone import (
    normalize_phone,
    is_valid_phone,
    format_phone_display,
    phones_match,
    strip_non_numeric
)
from utils.date import (
    parse_date,
    parse_datetime,
    is_before,
    is_after,
    days_between
)


class TestPhoneUtils:
    """Tests for phone number utilities."""
    
    def test_strip_non_numeric(self):
        """Test stripping non-numeric characters."""
        assert strip_non_numeric("(619) 555-1234") == "6195551234"
        assert strip_non_numeric("619-555-1234") == "6195551234"
        assert strip_non_numeric("6195551234") == "6195551234"
        assert strip_non_numeric("") == ""
        assert strip_non_numeric(None) == ""
    
    def test_is_valid_phone(self):
        """Test phone number validation."""
        # Valid numbers
        assert is_valid_phone("(619) 555-1234") is True
        assert is_valid_phone("619-555-1234") is True
        assert is_valid_phone("6195551234") is True
        
        # Invalid area codes
        assert is_valid_phone("(999) 555-1234") is False
        assert is_valid_phone("(000) 555-1234") is False
        
        # Invalid lengths
        assert is_valid_phone("555-1234") is False
        assert is_valid_phone("1234567890123") is False
        
        # Empty/None
        assert is_valid_phone("") is False
        assert is_valid_phone(None) is False
    
    def test_normalize_phone(self):
        """Test phone number normalization."""
        assert normalize_phone("(619) 555-1234") == "16195551234"
        assert normalize_phone("619-555-1234") == "16195551234"
        assert normalize_phone("6195551234") == "16195551234"
        
        # Without country code
        assert normalize_phone("(619) 555-1234", add_country_code=False) == "6195551234"
        
        # Invalid numbers return None
        assert normalize_phone("invalid") is None
        assert normalize_phone("") is None
    
    def test_format_phone_display(self):
        """Test phone number display formatting."""
        assert format_phone_display("6195551234") == "(619) 555-1234"
        assert format_phone_display("16195551234") == "+1 (619) 555-1234"
    
    def test_phones_match(self):
        """Test phone number matching."""
        assert phones_match("(619) 555-1234", "619-555-1234") is True
        assert phones_match("(619) 555-1234", "(858) 555-1234") is False
        assert phones_match("invalid", "(619) 555-1234") is False


class TestDateUtils:
    """Tests for date utilities."""
    
    def test_parse_date_iso_format(self):
        """Test parsing ISO format dates."""
        result = parse_date("2024-01-15")
        assert result == date(2024, 1, 15)
    
    def test_parse_date_us_format(self):
        """Test parsing US format dates."""
        result = parse_date("01/15/2024", "%m/%d/%Y")
        assert result == date(2024, 1, 15)
    
    def test_parse_date_with_time(self):
        """Test parsing dates with time component."""
        result = parse_date("2024-01-15T10:30:00")
        assert result == date(2024, 1, 15)
        
        result = parse_date("2024-01-15 10:30:00")
        assert result == date(2024, 1, 15)
    
    def test_parse_date_from_datetime(self):
        """Test parsing from datetime object."""
        dt = datetime(2024, 1, 15, 10, 30, 0)
        result = parse_date(dt)
        assert result == date(2024, 1, 15)
    
    def test_parse_date_invalid(self):
        """Test parsing invalid dates."""
        assert parse_date(None) is None
        assert parse_date("") is None
        assert parse_date("invalid") is None
    
    def test_parse_datetime(self):
        """Test parsing datetime strings."""
        result = parse_datetime("2024-01-15T10:30:00")
        assert result == datetime(2024, 1, 15, 10, 30, 0)
        
        result = parse_datetime("2024-01-15 10:30:00")
        assert result == datetime(2024, 1, 15, 10, 30, 0)
    
    def test_is_before(self):
        """Test date comparison (before)."""
        assert is_before("2024-01-15", "2024-01-20") is True
        assert is_before("2024-01-20", "2024-01-15") is False
        assert is_before("2024-01-15", "2024-01-15") is False
    
    def test_is_after(self):
        """Test date comparison (after)."""
        assert is_after("2024-01-20", "2024-01-15") is True
        assert is_after("2024-01-15", "2024-01-20") is False
        assert is_after("2024-01-15", "2024-01-15") is False
    
    def test_days_between(self):
        """Test calculating days between dates."""
        assert days_between("2024-01-15", "2024-01-20") == 5
        assert days_between("2024-01-20", "2024-01-15") == -5
        assert days_between("2024-01-15", "2024-01-15") == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
