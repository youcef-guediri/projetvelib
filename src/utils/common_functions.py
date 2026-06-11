"""
Common utility functions used across the dashboard.
Contains helper functions for data manipulation and visualization.
"""

import pandas as pd
from typing import Any
import logging

from config import COLORS, LOW_AVAILABILITY_THRESHOLD

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def get_availability_color(num_bikes: int) -> str:
    """
    Get color based on bike availability.
    
    Args:
        num_bikes: Number of available bikes
        
    Returns:
        Color code string
    """
    if num_bikes == 0:
        return COLORS['empty']
    elif num_bikes <= LOW_AVAILABILITY_THRESHOLD:
        return COLORS['low']
    else:
        return COLORS['available']


def format_percentage(value: float, decimals: int = 1) -> str:
    """
    Format a number as percentage string.
    
    Args:
        value: Numeric value to format
        decimals: Number of decimal places
        
    Returns:
        Formatted percentage string
    """
    try:
        return f"{value:.{decimals}f}%"
    except (ValueError, TypeError):
        return "N/A"


def calculate_statistics(df: pd.DataFrame, column: str) -> dict[str, Any]:
    """
    Calculate basic statistics for a column.
    
    Args:
        df: DataFrame
        column: Column name
        
    Returns:
        Dictionary with statistics
    """
    if column not in df.columns:
        logger.warning(f"Column {column} not found in DataFrame")
        return {}

    try:
        return {
            'mean': float(df[column].mean()),
            'median': float(df[column].median()),
            'std': float(df[column].std()),
            'min': float(df[column].min()),
            'max': float(df[column].max()),
            'sum': float(df[column].sum())
        }
    except Exception as e:
        logger.error(f"Error calculating statistics: {e}")
        return {}


def filter_operational_stations(df: pd.DataFrame) -> pd.DataFrame:
    """
    Filter only operational stations.
    
    Args:
        df: DataFrame with station data
        
    Returns:
        Filtered DataFrame
    """
    if 'is_operational' in df.columns:
        return df[df['is_operational'] == 1].copy()
    elif all(col in df.columns for col in ['is_installed', 'is_renting', 'is_returning']):
        return df[
            (df['is_installed'] == 1) &
            (df['is_renting'] == 1) &
            (df['is_returning'] == 1)
        ].copy()
    else:
        logger.warning("Cannot filter operational stations - missing columns")
        return df.copy()


def get_top_stations(
    df: pd.DataFrame,
    column: str,
    n: int = 10,
    ascending: bool = False
) -> pd.DataFrame:
    """
    Get top N stations by a specific metric.
    
    Args:
        df: DataFrame with station data
        column: Column to sort by
        n: Number of top stations to return
        ascending: Sort order (False for descending)
        
    Returns:
        DataFrame with top N stations
    """
    if column not in df.columns:
        logger.warning(f"Column {column} not found")
        return pd.DataFrame()

    return df.nlargest(n, column) if not ascending else df.nsmallest(n, column)


def create_hover_text(row: pd.Series) -> str:
    """
    Create formatted hover text for map markers.
    
    Args:
        row: DataFrame row with station data
        
    Returns:
        Formatted HTML string for hover text
    """
    try:
        text = f"<b>{row.get('name', 'Unknown Station')}</b><br>"
        text += f"Station ID: {row.get('station_id', 'N/A')}<br>"
        text += f"Total bikes: {int(row.get('num_bikes_available', 0))}<br>"
        text += f"Mechanical: {int(row.get('mechanical_bikes', 0))}<br>"
        text += f"Electric: {int(row.get('ebikes', 0))}<br>"
        text += f"Available docks: {int(row.get('num_docks_available', 0))}<br>"
        text += f"Capacity: {int(row.get('capacity', 0))}"
        return text
    except Exception as e:
        logger.error(f"Error creating hover text: {e}")
        return "Station information unavailable"


def safe_divide(numerator: float, denominator: float, default: float = 0.0) -> float:
    """
    Safely divide two numbers, returning default if division by zero.
    
    Args:
        numerator: Numerator value
        denominator: Denominator value
        default: Default value to return if division fails
        
    Returns:
        Result of division or default value
    """
    try:
        if denominator == 0:
            return default
        return numerator / denominator
    except (TypeError, ValueError):
        return default


def categorize_availability(num_bikes: int) -> str:
    """
    Categorize station availability.
    
    Args:
        num_bikes: Number of available bikes
        
    Returns:
        Category string
    """
    if num_bikes == 0:
        return "Empty"
    elif num_bikes <= LOW_AVAILABILITY_THRESHOLD:
        return "Low"
    else:
        return "Available"


def get_bike_type_distribution(df: pd.DataFrame) -> dict[str, int]:
    """
    Calculate distribution of bike types.
    
    Args:
        df: DataFrame with bike data
        
    Returns:
        Dictionary with bike type counts
    """
    try:
        return {
            'mechanical': int(df['mechanical_bikes'].sum()) if 'mechanical_bikes' in df.columns else 0,
            'electric': int(df['ebikes'].sum()) if 'ebikes' in df.columns else 0,
            'total': int(df['num_bikes_available'].sum()) if 'num_bikes_available' in df.columns else 0
        }
    except Exception as e:
        logger.error(f"Error calculating bike distribution: {e}")
        return {'mechanical': 0, 'electric': 0, 'total': 0}


def format_large_number(num: int | float) -> str:
    """
    Format large numbers with thousands separator.
    
    Args:
        num: Number to format
        
    Returns:
        Formatted string
    """
    try:
        return f"{int(num):,}"
    except (ValueError, TypeError):
        return "N/A"


def check_required_columns(df: pd.DataFrame, required_columns: list[str]) -> bool:
    """
    Check if DataFrame has all required columns.
    
    Args:
        df: DataFrame to check
        required_columns: List of required column names
        
    Returns:
        True if all columns present, False otherwise
    """
    missing = [col for col in required_columns if col not in df.columns]
    if missing:
        logger.warning(f"Missing columns: {missing}")
        return False
    return True


if __name__ == "__main__":
    # Test the functions
    print("Testing common functions...")

    # Test color function
    print("\nAvailability colors:")
    print(f"0 bikes: {get_availability_color(0)}")
    print(f"3 bikes: {get_availability_color(3)}")
    print(f"10 bikes: {get_availability_color(10)}")

    # Test percentage formatting
    print("\nPercentage formatting:")
    print(f"75.5 -> {format_percentage(75.5)}")
    print(f"100 -> {format_percentage(100, 0)}")

    # Test categorization
    print("\nAvailability categories:")
    print(f"0 bikes: {categorize_availability(0)}")
    print(f"3 bikes: {categorize_availability(3)}")
    print(f"10 bikes: {categorize_availability(10)}")
