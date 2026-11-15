"""
Unit Tests: IoT Sensor Generator
Air Quality Monitoring – Real-Time Anomaly Detection Platform
"""

import pytest
from datetime import datetime
from ingestion.sensor_generator import AirQualitySensorGenerator, DEFAULT_STATIONS


def test_generator_initialization():
    generator = AirQualitySensorGenerator()
    assert len(generator.stations) == len(DEFAULT_STATIONS)
    assert generator.anomaly_probability == 0.05


def test_single_reading_schema():
    generator = AirQualitySensorGenerator(random_seed=123)
    reading = generator.generate_single_reading(force_anomaly=False)

    # Check top-level schema
    assert "sensor_id" in reading
    assert "timestamp" in reading
    assert "location" in reading
    assert "measurements" in reading
    assert "status" in reading

    # Check location schema
    assert "lat" in reading["location"]
    assert "lon" in reading["location"]
    assert isinstance(reading["location"]["lat"], float)
    assert isinstance(reading["location"]["lon"], float)

    # Check measurements schema
    meas = reading["measurements"]
    expected_pollutants = ["pm2_5", "pm10", "no2", "o3", "temperature", "humidity"]
    for p in expected_pollutants:
        assert p in meas
        assert isinstance(meas[p], (int, float))

    # Verify timestamp format ISO 8601
    dt = datetime.fromisoformat(reading["timestamp"].replace("Z", "+00:00"))
    assert dt is not None


def test_normal_reading_ranges():
    generator = AirQualitySensorGenerator(random_seed=456)
    for _ in range(20):
        reading = generator.generate_single_reading(force_anomaly=False)
        meas = reading["measurements"]
        assert 0.0 <= meas["pm2_5"] <= 100.0
        assert 0.0 <= meas["pm10"] <= 150.0
        assert 0.0 <= meas["no2"] <= 150.0
        assert 0.0 <= meas["o3"] <= 200.0
        assert -10.0 <= meas["temperature"] <= 50.0
        assert 10.0 <= meas["humidity"] <= 100.0


def test_forced_anomaly_generation():
    generator = AirQualitySensorGenerator(random_seed=789)
    reading = generator.generate_single_reading(force_anomaly=True)
    assert reading is not None
    meas = reading["measurements"]
    # Check that at least one measurement is elevated or flagged
    is_elevated = (
        meas["pm2_5"] >= 50.0 or
        meas["pm10"] >= 90.0 or
        meas["no2"] >= 150.0 or
        meas["o3"] >= 140.0 or
        reading["status"] == "warning" or
        meas["no2"] < 0.0
    )
    assert is_elevated


def test_batch_generation():
    generator = AirQualitySensorGenerator()
    batch = generator.generate_batch(n_samples=50)
    assert len(batch) == 50
    assert all("sensor_id" in item for item in batch)
