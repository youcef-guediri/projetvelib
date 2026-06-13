"""
Unit tests for common utility functions.
"""

import pytest
import pandas as pd
import numpy as np

from src.utils.common_functions import (
    get_availability_color,
    format_percentage,
    calculate_statistics,
    filter_operational_stations,
    get_top_stations,
    safe_divide,
    categorize_availability,
    get_bike_type_distribution,
    format_large_number,
    check_required_columns
)
from config import COLORS


class TestAvailabilityColor:
    """Tests for get_availability_color function."""
    
    def test_empty_station(self):
        """Test color for empty station."""
        assert get_availability_color(0) == COLORS['empty']
    
    def test_low_availability(self):
        """Test color for low availability."""
        assert get_availability_color(3) == COLORS['low']
        assert get_availability_color(5) == COLORS['low']
    
    def test_available(self):
        """Test color for available station."""
        assert get_availability_color(10) == COLORS['available']
        assert get_availability_color(20) == COLORS['available']


class TestFormatPercentage:
    """Tests for format_percentage function."""
    
    def test_normal_value(self):
        """Test formatting normal percentage."""
        assert format_percentage(75.5) == "75.5%"
        assert format_percentage(100.0) == "100.0%"
    
    def test_with_decimals(self):
        """Test formatting with different decimal places."""
        assert format_percentage(75.567, 2) == "75.57%"
        assert format_percentage(75.567, 0) == "76%"
    
    def test_invalid_value(self):
        """Test formatting invalid value."""
        assert format_percentage("invalid") == "N/A"
        assert format_percentage(None) == "N/A"


class TestCalculateStatistics:
    """Tests for calculate_statistics function."""
    
    def test_valid_column(self):
        """Test statistics calculation for valid column."""
        df = pd.DataFrame({'values': [1, 2, 3, 4, 5]})
        stats = calculate_statistics(df, 'values')
        
        assert stats['mean'] == 3.0
        assert stats['median'] == 3.0
        assert stats['min'] == 1
        assert stats['max'] == 5
        assert stats['sum'] == 15
    
    def test_invalid_column(self):
        """Test statistics calculation for invalid column."""
        df = pd.DataFrame({'values': [1, 2, 3]})
        stats = calculate_statistics(df, 'nonexistent')
        
        assert stats == {}


class TestFilterOperationalStations:
    """Tests for filter_operational_stations function."""
    
    def test_with_operational_column(self):
        """Test filtering with is_operational column."""
        df = pd.DataFrame({
            'station_id': [1, 2, 3],
            'is_operational': [1, 0, 1]
        })
        
        filtered = filter_operational_stations(df)
        assert len(filtered) == 2
        assert all(filtered['is_operational'] == 1)
    
    def test_with_status_columns(self):
        """Test filtering with status columns."""
        df = pd.DataFrame({
            'station_id': [1, 2, 3],
            'is_installed': [1, 1, 0],
            'is_renting': [1, 0, 1],
            'is_returning': [1, 1, 1]
        })
        
        filtered = filter_operational_stations(df)
        assert len(filtered) == 1


class TestSafeDivide:
    """Tests for safe_divide function."""
    
    def test_normal_division(self):
        """Test normal division."""
        assert safe_divide(10, 2) == 5.0
        assert safe_divide(7, 2) == 3.5
    
    def test_division_by_zero(self):
        """Test division by zero."""
        assert safe_divide(10, 0) == 0.0
        assert safe_divide(10, 0, default=999) == 999
    
    def test_invalid_inputs(self):
        """Test invalid inputs."""
        assert safe_divide("invalid", 2) == 0.0
        assert safe_divide(10, "invalid") == 0.0


class TestCategorizeAvailability:
    """Tests for categorize_availability function."""
    
    def test_empty(self):
        """Test empty category."""
        assert categorize_availability(0) == "Empty"
    
    def test_low(self):
        """Test low category."""
        assert categorize_availability(3) == "Low"
        assert categorize_availability(5) == "Low"
    
    def test_available(self):
        """Test available category."""
        assert categorize_availability(10) == "Available"
        assert categorize_availability(20) == "Available"


class TestGetBikeTypeDistribution:
    """Tests for get_bike_type_distribution function."""
    
    def test_valid_dataframe(self):
        """Test distribution calculation with valid data."""
        df = pd.DataFrame({
            'mechanical_bikes': [5, 10, 15],
            'ebikes': [3, 7, 11],
            'num_bikes_available': [8, 17, 26]
        })
        
        dist = get_bike_type_distribution(df)
        assert dist['mechanical'] == 30
        assert dist['electric'] == 21
        assert dist['total'] == 51
    
    def test_missing_columns(self):
        """Test distribution with missing columns."""
        df = pd.DataFrame({'other_column': [1, 2, 3]})
        dist = get_bike_type_distribution(df)
        
        assert dist['mechanical'] == 0
        assert dist['electric'] == 0
        assert dist['total'] == 0


class TestFormatLargeNumber:
    """Tests for format_large_number function."""
    
    def test_normal_numbers(self):
        """Test formatting normal numbers."""
        assert format_large_number(1000) == "1,000"
        assert format_large_number(1000000) == "1,000,000"
    
    def test_small_numbers(self):
        """Test formatting small numbers."""
        assert format_large_number(100) == "100"
        assert format_large_number(0) == "0"
    
    def test_invalid_input(self):
        """Test formatting invalid input."""
        assert format_large_number("invalid") == "N/A"
        assert format_large_number(None) == "N/A"


class TestCheckRequiredColumns:
    """Tests for check_required_columns function."""
    
    def test_all_columns_present(self):
        """Test when all required columns are present."""
        df = pd.DataFrame({
            'col1': [1, 2],
            'col2': [3, 4],
            'col3': [5, 6]
        })
        
        assert check_required_columns(df, ['col1', 'col2']) is True
    
    def test_missing_columns(self):
        """Test when some columns are missing."""
        df = pd.DataFrame({
            'col1': [1, 2],
            'col2': [3, 4]
        })
        
        assert check_required_columns(df, ['col1', 'col3']) is False


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
