"""
Module for cleaning and preprocessing Velib data.
Handles data merging, cleaning, and transformation.
"""

import pandas as pd
import numpy as np
from typing import Optional
from pathlib import Path
import logging

from config import CLEANED_DATA_FILE

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def clean_station_information(df: pd.DataFrame) -> pd.DataFrame:
    """
    Clean station information data.
    
    Args:
        df: Raw station information DataFrame
        
    Returns:
        Cleaned DataFrame
    """
    logger.info("Cleaning station information data...")

    # Create a copy to avoid modifying original
    df_clean = df.copy()

    # Convert station_id to string for consistent merging
    df_clean['station_id'] = df_clean['station_id'].astype(str)

    # Handle missing values in capacity
    if 'capacity' in df_clean.columns:
        df_clean['capacity'] = pd.to_numeric(df_clean['capacity'], errors='coerce')
        df_clean['capacity'] = df_clean['capacity'].fillna(0)

    # Ensure lat/lon are numeric
    if 'lat' in df_clean.columns:
        df_clean['lat'] = pd.to_numeric(df_clean['lat'], errors='coerce')
    if 'lon' in df_clean.columns:
        df_clean['lon'] = pd.to_numeric(df_clean['lon'], errors='coerce')

    # Remove rows with missing coordinates
    df_clean = df_clean.dropna(subset=['lat', 'lon'])

    # Clean station names (remove extra spaces)
    if 'name' in df_clean.columns:
        df_clean['name'] = df_clean['name'].str.strip()

    logger.info(f"Cleaned station information: {len(df_clean)} stations")
    return df_clean


def clean_station_status(df: pd.DataFrame) -> pd.DataFrame:
    """
    Clean station status data.
    
    Args:
        df: Raw station status DataFrame
        
    Returns:
        Cleaned DataFrame
    """
    logger.info("Cleaning station status data...")

    # Create a copy
    df_clean = df.copy()

    # Convert station_id to string for consistent merging
    df_clean['station_id'] = df_clean['station_id'].astype(str)

    # Ensure numeric columns are properly typed
    numeric_columns = [
        'num_bikes_available',
        'num_bikes_available_types/0/mechanical',
        'num_bikes_available_types/1/ebike',
        'num_docks_available',
        'is_installed',
        'is_returning',
        'is_renting'
    ]

    for col in numeric_columns:
        if col in df_clean.columns:
            df_clean[col] = pd.to_numeric(df_clean[col], errors='coerce')
            df_clean[col] = df_clean[col].fillna(0)

    # Rename columns for easier access
    column_mapping = {
        'num_bikes_available_types/0/mechanical': 'mechanical_bikes',
        'num_bikes_available_types/1/ebike': 'ebikes'
    }
    df_clean.rename(columns=column_mapping, inplace=True)

    logger.info(f"Cleaned station status: {len(df_clean)} stations")
    return df_clean


def merge_station_data(
    info_df: pd.DataFrame,
    status_df: pd.DataFrame
) -> pd.DataFrame:
    """
    Merge station information and status data.
    
    Args:
        info_df: Station information DataFrame
        status_df: Station status DataFrame
        
    Returns:
        Merged DataFrame
    """
    logger.info("Merging station data...")

    # Clean both dataframes
    info_clean = clean_station_information(info_df)
    status_clean = clean_station_status(status_df)

    # Merge on station_id
    merged_df = pd.merge(
        info_clean,
        status_clean,
        on='station_id',
        how='inner',
        suffixes=('_info', '_status')
    )

    logger.info(f"Merged data: {len(merged_df)} stations")

    return merged_df


def add_derived_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Add derived features for analysis.
    
    Args:
        df: Merged DataFrame
        
    Returns:
        DataFrame with additional features
    """
    logger.info("Adding derived features...")

    df_enhanced = df.copy()

    # Calculate availability percentage
    if 'num_bikes_available' in df_enhanced.columns and 'capacity' in df_enhanced.columns:
        df_enhanced['availability_rate'] = (
            df_enhanced['num_bikes_available'] / df_enhanced['capacity'] * 100
        ).round(2)
        df_enhanced['availability_rate'] = df_enhanced['availability_rate'].fillna(0)
        # Cap at 100% to handle data inconsistencies
        df_enhanced['availability_rate'] = df_enhanced['availability_rate'].clip(upper=100)

    # Calculate occupancy percentage
    if 'num_docks_available' in df_enhanced.columns and 'capacity' in df_enhanced.columns:
        df_enhanced['occupancy_rate'] = (
            (df_enhanced['capacity'] - df_enhanced['num_docks_available']) /
            df_enhanced['capacity'] * 100
        ).round(2)
        df_enhanced['occupancy_rate'] = df_enhanced['occupancy_rate'].fillna(0)

    # Add availability status category
    if 'num_bikes_available' in df_enhanced.columns:
        df_enhanced['availability_status'] = pd.cut(
            df_enhanced['num_bikes_available'],
            bins=[-np.inf, 0, 5, np.inf],
            labels=['Empty', 'Low', 'Available']
        )

    # Calculate ebike percentage
    if 'ebikes' in df_enhanced.columns and 'num_bikes_available' in df_enhanced.columns:
        df_enhanced['ebike_percentage'] = (
            df_enhanced['ebikes'] / df_enhanced['num_bikes_available'] * 100
        ).round(2)
        df_enhanced['ebike_percentage'] = df_enhanced['ebike_percentage'].fillna(0)

    # Add operational status
    if all(col in df_enhanced.columns for col in ['is_installed', 'is_renting', 'is_returning']):
        df_enhanced['is_operational'] = (
            (df_enhanced['is_installed'] == 1) &
            (df_enhanced['is_renting'] == 1) &
            (df_enhanced['is_returning'] == 1)
        ).astype(int)

    logger.info("Derived features added successfully")
    return df_enhanced


def process_and_save_data(
    info_df: pd.DataFrame,
    status_df: pd.DataFrame,
    output_path: Optional[Path] = None
) -> pd.DataFrame:
    """
    Complete data processing pipeline.
    
    Args:
        info_df: Station information DataFrame
        status_df: Station status DataFrame
        output_path: Optional path to save cleaned data
        
    Returns:
        Processed DataFrame
    """
    # Merge data
    merged_df = merge_station_data(info_df, status_df)

    # Add derived features
    processed_df = add_derived_features(merged_df)

    # Save to file if path provided
    if output_path is None:
        output_path = CLEANED_DATA_FILE

    try:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        processed_df.to_csv(output_path, index=False)
        logger.info(f"Processed data saved to {output_path}")
    except Exception as e:
        logger.error(f"Error saving processed data: {e}")

    return processed_df


if __name__ == "__main__":
    # Test the module
    from src.utils.get_data import get_all_data

    print("Testing data cleaning...")
    info_df, status_df = get_all_data(use_local=True)

    processed_df = process_and_save_data(info_df, status_df)

    print(f"\nProcessed data shape: {processed_df.shape}")
    print("\nColumns:")
    print(processed_df.columns.tolist())
    print("\nFirst rows:")
    print(processed_df.head())
    print("\nData types:")
    print(processed_df.dtypes)

# Made with Bob
