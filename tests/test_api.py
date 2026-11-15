"""
Unit Tests: FastAPI Prediction & Monitoring Endpoints
Air Quality Monitoring – Real-Time Anomaly Detection Platform
"""

import pytest
from fastapi.testclient import TestClient
from api.main import app

client = TestClient(app)


def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "HEALTHY"
    assert "uptime_seconds" in data
    assert "database_backend" in data


def test_predict_endpoint_valid():
    payload = {
        "sensor_id": "CAP_001",
        "timestamp": "2026-11-15T14:30:00Z",
        "location": {"lat": 48.8566, "lon": 2.3522},
        "measurements": {
            "pm2_5": 65.0,  # High
            "pm10": 110.0,
            "no2": 45.0,
            "o3": 80.0,
            "temperature": 22.0,
            "humidity": 60.0
        },
        "status": "active"
    }
    response = client.post("/predict", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["sensor_id"] == "CAP_001"
    assert "prediction_label" in data
    assert "prediction_status" in data
    assert "anomaly_probability" in data
    assert "latency_ms" in data
    assert isinstance(data["is_anomaly"], bool)


def test_predict_endpoint_validation_error():
    # Negative humidity should trigger Pydantic validation error (422)
    bad_payload = {
        "sensor_id": "CAP_001",
        "timestamp": "2026-11-15T14:30:00Z",
        "location": {"lat": 48.8566, "lon": 2.3522},
        "measurements": {
            "pm2_5": 12.0,
            "pm10": 20.0,
            "no2": 30.0,
            "o3": 40.0,
            "temperature": 20.0,
            "humidity": -99.0  # Invalid
        }
    }
    response = client.post("/predict", json=bad_payload)
    assert response.status_code == 422


def test_get_anomalies_endpoint():
    response = client.get("/anomalies?limit=10")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_get_measurements_endpoint():
    response = client.get("/measurements?limit=10")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_get_catalog_endpoint():
    response = client.get("/catalog")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_get_metrics_endpoint():
    response = client.get("/metrics")
    assert response.status_code == 200
    data = response.json()
    assert "predictions_total" in data
    assert "uptime_seconds" in data
