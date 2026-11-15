"""
End-to-End Pipeline Integration Test
Air Quality Monitoring – Real-Time Anomaly Detection Platform

Tests complete data flow across components:
[IoT Generator] ➔ [Data Cleaning] ➔ [Anomaly Rules] ➔ [Database Storage] ➔ [ML Inference] ➔ [API Verification]
"""

import pytest
from ingestion.sensor_generator import AirQualitySensorGenerator
from processing.data_cleaning import DataCleaner
from processing.anomaly_rules import AnomalyRulesEngine
from database.connection import db
from ml.predict import predictor
from fastapi.testclient import TestClient
from api.main import app


def test_full_end_to_end_pipeline():
    # 1. IoT Telemetry Generation
    generator = AirQualitySensorGenerator(random_seed=101)
    readings = [
        generator.generate_single_reading(force_anomaly=False),
        generator.generate_single_reading(force_anomaly=True)
    ]
    assert len(readings) == 2

    # 2. Cleaning & Validation
    cleaner = DataCleaner()
    cleaned_records = []
    for r in readings:
        cleaned, report = cleaner.clean_record(r)
        assert "measurements" in cleaned
        cleaned_records.append(cleaned)

    # 3. Business Rule Anomaly Evaluation
    rules_engine = AnomalyRulesEngine()
    detected_anomalies = []
    for cr in cleaned_records:
        anoms = rules_engine.evaluate(cr)
        if anoms:
            detected_anomalies.extend(anoms)

    assert len(detected_anomalies) >= 1

    # 4. Persistence in Database
    saved_ids = []
    for cr in cleaned_records:
        m_id = db.save_measurement(cr)
        assert m_id is not None
        saved_ids.append(m_id)

    for anom in detected_anomalies:
        a_id = db.save_anomaly(anom, measurement_id=saved_ids[-1])
        assert a_id is not None

    db.update_catalog_lineage(
        dataset="e2e_integration_test",
        source="Sensor Generator",
        step="E2E Pipeline Test",
        dest="air_quality_measurements",
        rows=len(cleaned_records),
        comp=100.0
    )

    # 5. Machine Learning Inference
    for cr in cleaned_records:
        pred = predictor.predict_single(cr)
        assert "prediction_label" in pred
        assert "anomaly_probability" in pred
        p_id = db.save_prediction(pred)
        assert p_id is not None

    # 6. API Verification via FastAPI Client
    client = TestClient(app)

    # Verify Health
    health_resp = client.get("/health")
    assert health_resp.status_code == 200

    # Verify Measurements
    meas_resp = client.get("/measurements?limit=10")
    assert meas_resp.status_code == 200
    assert len(meas_resp.json()) >= 2

    # Verify Anomalies
    anom_resp = client.get("/anomalies?limit=10")
    assert anom_resp.status_code == 200
    assert len(anom_resp.json()) >= 1

    # Verify Data Catalog
    cat_resp = client.get("/catalog")
    assert cat_resp.status_code == 200
    assert len(cat_resp.json()) >= 1
