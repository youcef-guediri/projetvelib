"""Tests d'intégration pour les pages du dashboard."""
import pytest
import pandas as pd
from src.pages.home import create_home_layout
from src.pages.analysis import create_analysis_layout
from src.pages.map_page import create_map_layout
from src.pages.insights import create_insights_layout


class TestPageLayouts:
    """Test que les pages se chargent correctement."""

    @pytest.fixture
    def sample_df(self):
        """Créer un DataFrame de test."""
        return pd.DataFrame({
            'station_id': ['1', '2', '3'],
            'name': ['Station A', 'Station B', 'Station C'],
            'num_bikes_available': [5, 10, 15],
            'num_docks_available': [8, 12, 20],
            'mechanical_bikes': [3, 6, 8],
            'ebikes': [2, 4, 7],
            'is_operational': [1, 1, 1],
            'is_installed': [1, 1, 1],
            'is_renting': [1, 1, 1],
            'is_returning': [1, 1, 1],
            'capacity': [13, 22, 35],
            'lat': [48.8, 48.9, 48.7],
            'lon': [2.3, 2.4, 2.2],
            'availability_rate': [38.5, 45.5, 42.9],
            'occupancy_rate': [61.5, 54.5, 57.1],
            'ebike_percentage': [40.0, 40.0, 46.7],
            'availability_status': ['Available', 'Available', 'Available'],
        })

    def test_home_layout_renders(self, sample_df):
        """Test que la page home se charge sans erreur."""
        layout = create_home_layout(sample_df)
        assert layout is not None
        assert hasattr(layout, 'children')

    def test_analysis_layout_renders(self, sample_df):
        """Test que la page analysis se charge."""
        layout = create_analysis_layout(sample_df)
        assert layout is not None
        assert hasattr(layout, 'children')

    def test_map_layout_renders(self, sample_df):
        """Test que la page map se charge."""
        layout = create_map_layout(sample_df)
        assert layout is not None
        assert hasattr(layout, 'children')

    def test_insights_layout_renders(self, sample_df):
        """Test que la page insights se charge."""
        layout = create_insights_layout(sample_df)
        assert layout is not None
        assert hasattr(layout, 'children')
