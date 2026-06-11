
"""
Module for SQLite database operations.
Handles data storage and retrieval for the Velib Dashboard.
"""

import sqlite3
import pandas as pd
from pathlib import Path
from typing import Optional
import logging

from config import DATA_DIR

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Database path
DB_PATH = DATA_DIR / "velib_data.db"


def init_database() -> None:
    """
    Initialize the SQLite database with required tables.
    """
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Create stations table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS stations (
                station_id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                lat REAL NOT NULL,
                lon REAL NOT NULL,
                capacity INTEGER NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create station_status table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS station_status (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                station_id TEXT NOT NULL,
                num_bikes_available INTEGER NOT NULL,
                mechanical_bikes INTEGER NOT NULL,
                ebikes INTEGER NOT NULL,
                num_docks_available INTEGER NOT NULL,
                is_installed INTEGER NOT NULL,
                is_renting INTEGER NOT NULL,
                is_returning INTEGER NOT NULL,
                last_reported TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (station_id) REFERENCES stations(station_id)
            )
        """)
        
        # Create index for faster queries
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_station_status_station_id 
            ON station_status(station_id)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_station_status_last_reported 
            ON station_status(last_reported)
        """)
        
        conn.commit()
        conn.close()
        logger.info(f"Database initialized at {DB_PATH}")
        
    except Exception as e:
        logger.error(f"Error initializing database: {e}")
        raise


def save_stations_to_db(df: pd.DataFrame) -> None:
    """
    Save station information to database.
    
    Args:
        df: DataFrame with station information
    """
    try:
        conn = sqlite3.connect(DB_PATH)
        
        # Select only required columns
        stations_df = df[['station_id', 'name', 'lat', 'lon', 'capacity']].copy()
        stations_df = stations_df.drop_duplicates(subset=['station_id'])
        
        # Save to database (replace if exists)
        stations_df.to_sql('stations', conn, if_exists='replace', index=False)
        
        conn.close()
        logger.info(f"Saved {len(stations_df)} stations to database")
        
    except Exception as e:
        logger.error(f"Error saving stations to database: {e}")
        raise


def save_status_to_db(df: pd.DataFrame) -> None:
    """
    Save station status to database.
    
    Args:
        df: DataFrame with station status
    """
    try:
        conn = sqlite3.connect(DB_PATH)
        
        # Select required columns
        status_columns = [
            'station_id', 'num_bikes_available', 'mechanical_bikes', 
            'ebikes', 'num_docks_available', 'is_installed', 
            'is_renting', 'is_returning'
        ]
        
        status_df = df[status_columns].copy()
        
        # Append to database
        status_df.to_sql('station_status', conn, if_exists='append', index=False)
        
        conn.close()
        logger.info(f"Saved {len(status_df)} status records to database")
        
    except Exception as e:
        logger.error(f"Error saving status to database: {e}")
        raise


def load_stations_from_db() -> Optional[pd.DataFrame]:
    """
    Load station information from database.
    
    Returns:
        DataFrame with station information or None if error
    """
    try:
        conn = sqlite3.connect(DB_PATH)
        df = pd.read_sql_query("SELECT * FROM stations", conn)
        conn.close()
        logger.info(f"Loaded {len(df)} stations from database")
        return df
        
    except Exception as e:
        logger.error(f"Error loading stations from database: {e}")
        return None


def load_latest_status_from_db() -> Optional[pd.DataFrame]:
    """
    Load latest station status from database.
    
    Returns:
        DataFrame with latest status or None if error
    """
    try:
        conn = sqlite3.connect(DB_PATH)
        
        # Get latest status for each station
        query = """
            SELECT s1.*
            FROM station_status s1
            INNER JOIN (
                SELECT station_id, MAX(last_reported) as max_date
                FROM station_status
                GROUP BY station_id
            ) s2
            ON s1.station_id = s2.station_id 
            AND s1.last_reported = s2.max_date
        """
        
        df = pd.read_sql_query(query, conn)
        conn.close()
        logger.info(f"Loaded latest status for {len(df)} stations from database")
        return df
        
    except Exception as e:
        logger.error(f"Error loading status from database: {e}")
        return None


def get_merged_data_from_db() -> Optional[pd.DataFrame]:
    """
    Get merged station information and status from database.
    
    Returns:
        Merged DataFrame or None if error
    """
    try:
        stations_df = load_stations_from_db()
        status_df = load_latest_status_from_db()
        
        if stations_df is None or status_df is None:
            return None
        
        # Merge dataframes
        merged_df = pd.merge(
            stations_df,
            status_df,
            on='station_id',
            how='inner'
        )
        
        logger.info(f"Merged data: {len(merged_df)} stations")
        return merged_df
        
    except Exception as e:
        logger.error(f"Error merging data from database: {e}")
        return None


def database_exists() -> bool:
    """
    Check if database file exists.
    
    Returns:
        True if database exists, False otherwise
    """
    return DB_PATH.exists()


if __name__ == "__main__":
    # Test database operations
    print("Initializing database...")
    init_database()
    print("Database initialized successfully!")
