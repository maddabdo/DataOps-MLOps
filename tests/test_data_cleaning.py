"""
Unit Tests: Data Cleaning & Validation
Air Quality Monitoring – Real-Time Anomaly Detection Platform
"""

import pytest
from processing.data_cleaning import DataCleaner


@pytest.fixture
def cleaner():
    return DataCleaner()


@pytest.fixture
def valid_payload():
    return {
        "sensor_id": "CAP_001",
        "timestamp": "2026-11-15T14:30:00Z",
        "location": {"lat": 48.8566, "lon": 2.3522},
        "measurements": {
            "pm2_5": 12.5,
            "pm10": 25.3,
            "no2": 40.2,
            "o3": 80.1,
            "temperature": 22.5,
            "humidity": 65.0
        },
        "status": "active"
    }


def test_validate_schema_valid(cleaner, valid_payload):
    is_valid, err = cleaner.validate_schema(valid_payload)
    assert is_valid is True
    assert err is None


def test_validate_schema_missing_key(cleaner, valid_payload):
    del valid_payload["sensor_id"]
    is_valid, err = cleaner.validate_schema(valid_payload)
    assert is_valid is False
    assert "Missing top-level key" in err


def test_validate_schema_missing_measurement(cleaner, valid_payload):
    del valid_payload["measurements"]["pm2_5"]
    is_valid, err = cleaner.validate_schema(valid_payload)
    assert is_valid is False
    assert "Missing measurement key" in err


def test_clean_record_clipping(cleaner, valid_payload):
    # Pass negative NO2 and extreme PM2.5
    valid_payload["measurements"]["no2"] = -50.0
    valid_payload["measurements"]["pm2_5"] = 999.0

    cleaned, report = cleaner.clean_record(valid_payload)
    assert cleaned["measurements"]["no2"] == 0.0  # Clipped to min bound
    assert cleaned["measurements"]["pm2_5"] == 500.0  # Clipped to max bound
    assert report["is_clean"] is False
    assert len(report["sanitized_fields"]) == 2


def test_deduplication(cleaner, valid_payload):
    assert cleaner.check_and_deduplicate(valid_payload) is True
    # Second insertion with same key should be detected as duplicate
    assert cleaner.check_and_deduplicate(valid_payload) is False
