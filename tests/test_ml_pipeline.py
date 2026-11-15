"""
Unit Tests: Machine Learning Pipeline
Air Quality Monitoring – Real-Time Anomaly Detection Platform
"""

import pytest
import os
import numpy as np
from ml.preprocessing import extract_features_from_dict, define_ground_truth_label, prepare_dataset, FEATURE_NAMES
from ml.train import train_and_compare_models
from ml.predict import AnomalyPredictor


@pytest.fixture
def sample_reading():
    return {
        "sensor_id": "CAP_001",
        "timestamp": "2026-11-15T15:30:00Z",
        "location": {"lat": 48.8566, "lon": 2.3522},
        "measurements": {
            "pm2_5": 58.2,
            "pm10": 105.0,
            "no2": 45.0,
            "o3": 65.0,
            "temperature": 23.0,
            "humidity": 55.0
        },
        "status": "active"
    }


def test_feature_extraction(sample_reading):
    features = extract_features_from_dict(sample_reading)
    for col in FEATURE_NAMES:
        assert col in features
        assert isinstance(features[col], (int, float))

    assert "pm_ratio" in features
    assert "traffic_proxy" in features
    assert "hour_sin" in features
    assert "hour_cos" in features


def test_ground_truth_labeling(sample_reading):
    features = extract_features_from_dict(sample_reading)
    # PM2.5 is 58.2 >= 50.0 -> should be labeled as Anomaly (1)
    label = define_ground_truth_label(features)
    assert label == 1

    normal_features = features.copy()
    normal_features["pm2_5"] = 10.0
    normal_features["pm10"] = 20.0
    normal_features["no2"] = 30.0
    normal_features["o3"] = 40.0
    assert define_ground_truth_label(normal_features) == 0


def test_prepare_dataset():
    from ingestion.sensor_generator import AirQualitySensorGenerator
    gen = AirQualitySensorGenerator(random_seed=42)
    telemetry = gen.generate_batch(n_samples=100)

    X_tr, X_te, y_tr, y_te, scaler = prepare_dataset(telemetry)
    assert X_tr.shape[1] == len(FEATURE_NAMES)
    assert X_te.shape[1] == len(FEATURE_NAMES)
    assert len(X_tr) == 80
    assert len(X_te) == 20


def test_train_and_compare():
    results = train_and_compare_models(n_samples=200)
    assert "best_algorithm" in results
    assert results["best_algorithm"] in ["RandomForest", "GradientBoosting"]
    assert "best_metrics" in results
    assert results["best_metrics"]["f1_score"] >= 0.70


def test_predictor_single(sample_reading):
    pred = AnomalyPredictor()
    result = pred.predict_single(sample_reading)
    assert result["sensor_id"] == "CAP_001"
    assert result["prediction_label"] in [0, 1]
    assert 0.0 <= result["anomaly_probability"] <= 1.0
    assert result["latency_ms"] >= 0.0
