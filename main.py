"""
Main entry point for the Velib Dashboard application.
Run this file to start the dashboard: python main.py
"""

import sys
import importlib.util
from pathlib import Path

# Check required packages
REQUIRED_PACKAGES = [
    'dash',
    'dash_bootstrap_components',
    'plotly',
    'pandas',
    'numpy',
    'requests'
]

def check_packages() -> bool:
    """
    Check if all required packages are installed.
    
    Returns:
        True if all packages are available, False otherwise
    """
    missing_packages = []
    
    for package in REQUIRED_PACKAGES:
        spec = importlib.util.find_spec(package)
        if spec is None:
            missing_packages.append(package)
    
    if missing_packages:
        print("❌ Missing required packages:")
        for package in missing_packages:
            print(f"   - {package}")
        print("\n💡 Install missing packages with:")
        print("   python -m pip install -r requirements.txt")
        return False
    
    return True


if not check_packages():
    sys.exit(1)

# Import after checking packages
from dash import Dash, html, dcc, Input, Output
import dash_bootstrap_components as dbc
import logging

from config import (
    DASHBOARD_HOST,
    DASHBOARD_PORT,
    DEBUG_MODE,
    CLEANED_DATA_FILE,
    USE_DATABASE
)
from src.utils.get_data import get_all_data
from src.utils.clean_data import process_and_save_data
from src.utils.database import (
    init_database,
    database_exists,
    save_stations_to_db,
    save_status_to_db,
    get_merged_data_from_db
)
from src.components.header import create_header
from src.components.footer import create_footer
from src.components.navbar import create_navbar
from src.pages.home import create_home_layout
from src.pages.analysis import create_analysis_layout
from src.pages.map_page import create_map_layout
from src.pages.insights import create_maintenance_layout
from src.pages.insights_callbacks import register_insights_callbacks
from src.pages.about import create_about_layout

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def load_and_prepare_data():
    """
    Load and prepare data for the dashboard.
    
    Returns:
        Processed DataFrame
    """
    logger.info("Loading data...")
    
    try:
        # Try to use database first if enabled
        if USE_DATABASE and database_exists():
            logger.info("Loading data from SQLite database...")
            df = get_merged_data_from_db()
            if df is not None and len(df) > 0:
                logger.info(f"Loaded {len(df)} stations from database")
                # Add derived features
                from src.utils.clean_data import add_derived_features
                df = add_derived_features(df)
                return df
            else:
                logger.warning("Database is empty or error occurred")
        
        # Fallback to CSV files
        if CLEANED_DATA_FILE.exists():
            logger.info(f"Loading cleaned data from {CLEANED_DATA_FILE}")
            import pandas as pd
            df = pd.read_csv(CLEANED_DATA_FILE)
            logger.info(f"Loaded {len(df)} stations from cleaned data")
        else:
            logger.info("Cleaned data not found. Processing raw data...")
            info_df, status_df = get_all_data(use_local=True)
            df = process_and_save_data(info_df, status_df)
            logger.info(f"Processed and saved {len(df)} stations")
            
            # Save to database if enabled
            if USE_DATABASE:
                logger.info("Initializing and populating database...")
                init_database()
                save_stations_to_db(df)
                save_status_to_db(df)
                logger.info("Data saved to database")
        
        return df
    
    except Exception as e:
        logger.error(f"Error loading data: {e}")
        raise


def create_app():
    """
    Create and configure the Dash application.
    
    Returns:
        Configured Dash app
    """
    # Initialize the app with Bootstrap theme
    app = Dash(
        __name__,
        external_stylesheets=[dbc.themes.BOOTSTRAP],
        suppress_callback_exceptions=True,
        title="Vélib' Dashboard"
    )
    
    # Load data
    df = load_and_prepare_data()
    
    # Define the app layout
    app.layout = html.Div([
        dcc.Location(id='url', refresh=False),
        create_navbar(),
        dbc.Container([
            html.Div(id='page-content'),
            create_footer()
        ], fluid=True, style={'minHeight': '80vh'})
    ])
    
    # Callback for page navigation
    @app.callback(
        Output('page-content', 'children'),
        Input('url', 'pathname')
    )
    def display_page(pathname):
        """
        Display the appropriate page based on URL pathname.
        
        Args:
            pathname: URL pathname
            
        Returns:
            Page layout
        """
        if pathname == '/analysis':
            return create_analysis_layout(df)
        elif pathname == '/map':
            return create_map_layout(df)
        elif pathname == '/insights':
            return create_maintenance_layout(df)
        elif pathname == '/about':
            return create_about_layout()
        else:  # Default to home page
            return create_home_layout(df)
    
    # Register insights page callbacks for filter functionality
    register_insights_callbacks(app, df)
    
    return app


def main():
    """
    Main function to run the dashboard.
    """
    try:
        logger.info("=" * 60)
        logger.info("Starting Vélib' Dashboard")
        logger.info("=" * 60)
        
        # Create the app
        app = create_app()
        
        # Run the server
        logger.info(f"Dashboard running on http://{DASHBOARD_HOST}:{DASHBOARD_PORT}")
        logger.info("Press Ctrl+C to stop the server")
        logger.info("=" * 60)
        
        app.run(
            host=DASHBOARD_HOST,
            port=DASHBOARD_PORT,
            debug=DEBUG_MODE
        )
        
    except KeyboardInterrupt:
        logger.info("\n" + "=" * 60)
        logger.info("Dashboard stopped by user")
        logger.info("=" * 60)
    except Exception as e:
        logger.error(f"Error running dashboard: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

