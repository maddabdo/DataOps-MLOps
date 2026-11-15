#!/usr/bin/env python3
"""
Machine Learning Preprocessing & Feature Engineering
Air Quality Monitoring – Real-Time Anomaly Detection Platform

Implements:
- Domain feature extraction (PM ratio, traffic proxy, circadian harmonics)
- Leak-free chronological time-series splitting (80% train / 20% test)
- StandardScaler fitted strictly on train split
"""

import os
import math
import json
import logging
from datetime import datetime
from typing import Tuple, List, Dict, Any, Optional

import numpy as np
import pandas as pd
# Resilient StandardScaler compatible across all Python versions
class StandardScaler:
    """Standardize features by removing the mean and scaling to unit variance."""
    def __init__(self):
        self.mean_ = None
        self.scale_ = None

    def fit(self, X: np.ndarray):
        X = np.array(X, dtype=np.float64)
        self.mean_ = np.mean(X, axis=0)
        self.scale_ = np.std(X, axis=0)
        # Avoid division by zero
        self.scale_[self.scale_ == 0.0] = 1.0
        return self

    def transform(self, X: np.ndarray) -> np.ndarray:
        X = np.array(X, dtype=np.float64)
        return (X - self.mean_) / self.scale_

    def fit_transform(self, X: np.ndarray) -> np.ndarray:
        return self.fit(X).transform(X)
import joblib

logger = logging.getLogger("MLPreprocessing")

FEATURE_NAMES = [
    "pm2_5",
    "pm10",
    "no2",
    "o3",
    "temperature",
    "humidity",
    "pm_ratio",
    "traffic_proxy",
    "hour_sin",
    "hour_cos"
]


def extract_features_from_dict(reading: Dict[str, Any]) -> Dict[str, float]:
    """
    Transforms a single telemetry JSON payload into a numerical feature dictionary.
    """
    meas = reading["measurements"]
    pm2_5 = float(meas["pm2_5"])
    pm10 = float(meas["pm10"])
    no2 = float(meas["no2"])
    o3 = float(meas["o3"])
    temp = float(meas["temperature"])
    humidity = float(meas["humidity"])

    # Parse hour for circadian features
    try:
        ts_str = reading["timestamp"].replace("Z", "+00:00")
        dt = datetime.fromisoformat(ts_str)
        hour = dt.hour + dt.minute / 60.0
    except Exception:
        hour = 12.0

    pm_ratio = pm2_5 / (pm10 + 1e-5)
    traffic_proxy = (no2 * pm10) / 1000.0
    hour_sin = math.sin(2.0 * math.pi * hour / 24.0)
    hour_cos = math.cos(2.0 * math.pi * hour / 24.0)

    return {
        "pm2_5": pm2_5,
        "pm10": pm10,
        "no2": no2,
        "o3": o3,
        "temperature": temp,
        "humidity": humidity,
        "pm_ratio": round(pm_ratio, 4),
        "traffic_proxy": round(traffic_proxy, 4),
        "hour_sin": round(hour_sin, 4),
        "hour_cos": round(hour_cos, 4)
    }


def define_ground_truth_label(row: Dict[str, float]) -> int:
    """
    Assigns simulated supervised label (1: Anomaly, 0: Normal) based on WHO/EU rules:
    - PM2.5 >= 50.0 µg/m³
    - PM10 >= 100.0 µg/m³
    - NO2 >= 200.0 µg/m³
    - O3 >= 180.0 µg/m³
    """
    if (
        row["pm2_5"] >= 50.0 or
        row["pm10"] >= 100.0 or
        row["no2"] >= 200.0 or
        row["o3"] >= 180.0 or
        row["pm2_5"] < 0.0 or
        row["no2"] < 0.0
    ):
        return 1
    return 0


def prepare_dataset(
    readings: List[Dict[str, Any]],
    scaler_path: Optional[str] = None
) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, StandardScaler]:
    """
    Converts list of readings to train/test matrices with leak-free chronological split.
    """
    rows = []
    labels = []

    for r in readings:
        feats = extract_features_from_dict(r)
        y = define_ground_truth_label(feats)
        rows.append([feats[col] for col in FEATURE_NAMES])
        labels.append(y)

    X = np.array(rows, dtype=np.float32)
    y = np.array(labels, dtype=np.int32)

    # Chronological Split (80% Train, 20% Test)
    split_idx = int(len(X) * 0.8)
    X_train, X_test = X[:split_idx], X[split_idx:]
    y_train, y_test = y[:split_idx], y[split_idx:]

    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    if scaler_path:
        os.makedirs(os.path.dirname(os.path.abspath(scaler_path)), exist_ok=True)
        joblib.dump(scaler, scaler_path)
        logger.info(f"Fitted scaler saved to {scaler_path}")

    return X_train_scaled, X_test_scaled, y_train, y_test, scaler


if __name__ == "__main__":
    from ingestion.sensor_generator import AirQualitySensorGenerator
    gen = AirQualitySensorGenerator()
    data = gen.generate_batch(n_samples=500)
    X_tr, X_te, y_tr, y_te, sc = prepare_dataset(data)
    print(f"Dataset prepared successfully:")
    print(f"X_train shape: {X_tr.shape}, Anomalies in train: {sum(y_tr)} ({sum(y_tr)/len(y_tr)*100:.1f}%)")
    print(f"X_test shape:  {X_te.shape}, Anomalies in test:  {sum(y_te)} ({sum(y_te)/len(y_te)*100:.1f}%)")
