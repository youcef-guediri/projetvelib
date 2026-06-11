"""Tests de validation complète des données."""
import pytest
from src.utils.clean_data import (
    clean_station_information,
    clean_station_status,
    merge_station_data,
    add_derived_features,
)
from src.utils.get_data import get_all_data


class TestDataValidation:
    """Test la validation complète des données."""

    @pytest.fixture
    def raw_data(self):
        """Charger les données brutes."""
        return get_all_data(use_local=True)

    def test_clean_station_information(self, raw_data):
        """Test le nettoyage des infos stations."""
        info_df, _ = raw_data
        cleaned = clean_station_information(info_df)
        assert not cleaned.empty
        assert 'station_id' in cleaned.columns
        assert len(cleaned) <= len(info_df)  # May remove rows with missing coords

    def test_clean_station_status(self, raw_data):
        """Test le nettoyage du statut stations."""
        _, status_df = raw_data
        cleaned = clean_station_status(status_df)
        assert not cleaned.empty
        assert 'station_id' in cleaned.columns
        assert len(cleaned) == len(status_df)

    def test_merge_preserves_data(self, raw_data):
        """Test que la fusion préserve les données."""
        info_df, status_df = raw_data
        info_clean = clean_station_information(info_df)
        status_clean = clean_station_status(status_df)
        merged = merge_station_data(info_clean, status_clean)

        assert len(merged) <= len(info_clean)
        assert 'num_bikes_available' in merged.columns
        assert 'name' in merged.columns

    def test_features_added(self, raw_data):
        """Test que les features sont bien ajoutées."""
        info_df, status_df = raw_data
        info_clean = clean_station_information(info_df)
        status_clean = clean_station_status(status_df)
        merged = merge_station_data(info_clean, status_clean)
        final = add_derived_features(merged)

        expected_features = [
            'availability_rate',
            'occupancy_rate',
            'is_operational',
            'availability_status',
        ]
        for feature in expected_features:
            assert feature in final.columns, f"Feature '{feature}' not found"

    def test_data_quality_no_nulls_critical(self, raw_data):
        """Test qu'il n'y a pas de nulls dans les colonnes critiques."""
        info_df, status_df = raw_data
        info_clean = clean_station_information(info_df)
        status_clean = clean_station_status(status_df)
        merged = merge_station_data(info_clean, status_clean)
        final = add_derived_features(merged)

        critical_cols = [
            'station_id',
            'name',
            'num_bikes_available',
            'num_docks_available',
        ]
        for col in critical_cols:
            null_count = final[col].isna().sum()
            assert null_count == 0, f"Column '{col}' has {null_count} nulls"

    def test_data_consistency(self, raw_data):
        """Test la cohérence des données."""
        info_df, status_df = raw_data
        info_clean = clean_station_information(info_df)
        status_clean = clean_station_status(status_df)
        merged = merge_station_data(info_clean, status_clean)
        final = add_derived_features(merged)

        assert (final['num_bikes_available'] >= 0).all()
        assert (final['num_docks_available'] >= 0).all()
        assert (final['availability_rate'] >= 0).all()
        assert (final['availability_rate'] <= 100).all()
