"""
Unit Tests: Business Rule Anomaly Detection Engine
Air Quality Monitoring – Real-Time Anomaly Detection Platform
"""

import pytest
from processing.anomaly_rules import AnomalyRulesEngine


@pytest.fixture
def engine():
    return AnomalyRulesEngine()


def test_normal_reading_no_anomaly(engine):
    reading = {
        "sensor_id": "CAP_001",
        "timestamp": "2026-11-15T10:00:00Z",
        "measurements": {
            "pm2_5": 12.0,
            "pm10": 24.0,
            "no2": 35.0,
            "o3": 45.0
        }
    }
    anomalies = engine.evaluate(reading)
    assert len(anomalies) == 0


def test_pm25_high_pollution_alert(engine):
    reading = {
        "sensor_id": "CAP_001",
        "timestamp": "2026-11-15T11:00:00Z",
        "measurements": {
            "pm2_5": 65.0,  # >= 50.0 alert
            "pm10": 45.0,
            "no2": 40.0,
            "o3": 50.0
        }
    }
    anomalies = engine.evaluate(reading)
    assert len(anomalies) == 1
    assert anomalies[0]["anomaly_type"] == "PM2_5_HIGH_POLLUTION"
    assert anomalies[0]["severity"] == "HIGH"


def test_pm25_critical_exceedance(engine):
    reading = {
        "sensor_id": "CAP_001",
        "timestamp": "2026-11-15T12:00:00Z",
        "measurements": {
            "pm2_5": 95.0,  # >= 80.0 critical
            "pm10": 45.0,
            "no2": 40.0,
            "o3": 50.0
        }
    }
    anomalies = engine.evaluate(reading)
    assert any(a["severity"] == "CRITICAL" for a in anomalies)


def test_no2_traffic_smog_alert(engine):
    reading = {
        "sensor_id": "CAP_002",
        "timestamp": "2026-11-15T18:00:00Z",
        "measurements": {
            "pm2_5": 20.0,
            "pm10": 40.0,
            "no2": 215.0,  # >= 200.0 hourly alert
            "o3": 40.0
        }
    }
    anomalies = engine.evaluate(reading)
    assert any(a["anomaly_type"] == "NO2_HOURLY_ALERT" for a in anomalies)


def test_o3_summer_ozone_alert(engine):
    reading = {
        "sensor_id": "CAP_003",
        "timestamp": "2026-11-15T15:00:00Z",
        "measurements": {
            "pm2_5": 15.0,
            "pm10": 30.0,
            "no2": 25.0,
            "o3": 195.0  # >= 180.0 information threshold
        }
    }
    anomalies = engine.evaluate(reading)
    assert any(a["anomaly_type"] == "O3_INFORMATION_THRESHOLD" for a in anomalies)


def test_delta_spike_detection(engine):
    reading_1 = {
        "sensor_id": "CAP_004",
        "timestamp": "2026-11-15T14:00:00Z",
        "measurements": {"pm2_5": 15.0, "pm10": 30.0, "no2": 20.0, "o3": 30.0}
    }
    engine.evaluate(reading_1)

    reading_2 = {
        "sensor_id": "CAP_004",
        "timestamp": "2026-11-15T14:05:00Z",
        "measurements": {"pm2_5": 65.0, "pm10": 30.0, "no2": 20.0, "o3": 30.0}  # Delta = 50.0 >= 40.0
    }
    anomalies = engine.evaluate(reading_2)
    types = [a["anomaly_type"] for a in anomalies]
    assert "PM2_5_DELTA_SPIKE" in types
