"""
Unit Tests: Database Storage Layer
Air Quality Monitoring – Real-Time Anomaly Detection Platform
"""

import pytest
import os
from database.connection import DatabaseManager


@pytest.fixture
def test_db(tmp_path):
    db_file = tmp_path / "test_air_quality.db"
    manager = DatabaseManager(db_url=f"sqlite:///{db_file}")
    manager.engine.db_path = str(db_file)
    manager.engine.init_schema()
    manager.engine.seed_sensors()
    return manager


def test_seed_sensors(test_db):
    recs = test_db.get_recent_measurements(limit=10)
    # Check that query executes without syntax error
    assert isinstance(recs, list)


def test_save_measurement(test_db):
    payload = {
        "sensor_id": "CAP_001",
        "timestamp": "2026-11-15T12:00:00Z",
        "measurements": {
            "pm2_5": 14.2,
            "pm10": 28.5,
            "no2": 35.1,
            "o3": 65.4,
            "temperature": 21.0,
            "humidity": 60.0
        },
        "status": "active"
    }
    m_id = test_db.save_measurement(payload)
    assert m_id is not None
    assert m_id > 0

    recent = test_db.get_recent_measurements(sensor_id="CAP_001", limit=1)
    assert len(recent) == 1
    assert recent[0]["pm2_5"] == 14.2


def test_save_anomaly(test_db):
    anomaly = {
        "sensor_id": "CAP_001",
        "timestamp": "2026-11-15T12:00:00Z",
        "anomaly_type": "PM2_5_ALERT",
        "severity": "HIGH",
        "rule_triggered": "PM2.5 >= 50.0",
        "value_observed": 55.4,
        "threshold": 50.0
    }
    a_id = test_db.save_anomaly(anomaly)
    assert a_id is not None
    assert a_id > 0

    anomalies = test_db.get_anomalies(limit=5)
    assert len(anomalies) >= 1
    assert anomalies[0]["anomaly_type"] == "PM2_5_ALERT"


def test_save_prediction(test_db):
    pred = {
        "model_name": "RandomForest",
        "model_version": "1.0",
        "sensor_id": "CAP_001",
        "timestamp": "2026-11-15T12:00:00Z",
        "prediction_label": 1,
        "anomaly_probability": 0.88,
        "is_anomaly": True,
        "actual_label": 1
    }
    p_id = test_db.save_prediction(pred)
    assert p_id is not None
    assert p_id > 0


def test_catalog_lineage(test_db):
    test_db.update_catalog_lineage(
        dataset="test_batch",
        source="unit_test",
        step="test_step",
        dest="test_table",
        rows=10,
        comp=100.0
    )
    catalog = test_db.get_catalog_lineage()
    assert len(catalog) >= 1
    assert catalog[0]["dataset_name"] == "test_batch"
