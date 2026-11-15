"""
Unit Tests: Spark & Python Streaming Micro-batch Processor
Air Quality Monitoring – Real-Time Anomaly Detection Platform
"""

import pytest
from processing.spark_streaming import SparkStreamProcessor


@pytest.fixture
def processor():
    return SparkStreamProcessor()


def test_process_single_message_normal(processor):
    normal_msg = {
        "sensor_id": "CAP_001",
        "timestamp": "2026-11-15T10:00:00Z",
        "location": {"lat": 48.8566, "lon": 2.3522},
        "measurements": {
            "pm2_5": 12.0, "pm10": 25.0, "no2": 35.0,
            "o3": 40.0, "temperature": 20.0, "humidity": 65.0
        },
        "status": "active"
    }
    result = processor.process_message(normal_msg)
    assert result["has_anomaly"] is False
    assert result["quality_report"]["is_clean"] is True
    assert len(result["anomalies"]) == 0


def test_process_single_message_anomaly(processor):
    anom_msg = {
        "sensor_id": "CAP_002",
        "timestamp": "2026-11-15T11:00:00Z",
        "location": {"lat": 48.8530, "lon": 2.3698},
        "measurements": {
            "pm2_5": 85.0, "pm10": 160.0, "no2": 45.0,
            "o3": 50.0, "temperature": 21.0, "humidity": 60.0
        },
        "status": "active"
    }
    result = processor.process_message(anom_msg)
    assert result["has_anomaly"] is True
    assert len(result["anomalies"]) >= 1


def test_process_batch(processor):
    batch = [
        {
            "sensor_id": f"CAP_00{i}",
            "timestamp": f"2026-11-15T12:0{i}:00Z",
            "location": {"lat": 48.8566, "lon": 2.3522},
            "measurements": {"pm2_5": 10.0 + i * 20.0, "pm10": 20.0, "no2": 30.0, "o3": 40.0, "temperature": 20.0, "humidity": 50.0},
            "status": "active"
        }
        for i in range(1, 4)
    ]
    batch_res = processor.process_batch(batch)
    assert batch_res["batch_size"] == 3
    assert batch_res["processed_count"] == 3
    assert "anomaly_count" in batch_res
