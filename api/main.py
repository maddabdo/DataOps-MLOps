#!/usr/bin/env python3
"""
FastAPI Real-Time Prediction & Telemetry Service
Air Quality Monitoring – Real-Time Anomaly Detection Platform

Required endpoints:
- GET /health: Healthcheck & service status
- POST /predict: Real-time ML anomaly prediction with Pydantic validation
- GET /anomalies: Query detected anomalies with severity filters
- GET /measurements: Query historical sensor records
- GET /catalog: Data lineage & DataOps quality metadata
- GET /metrics: Operational performance counters
"""

import os
import sys
import time
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone

from fastapi import FastAPI, HTTPException, Query, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from database.connection import db
from ml.predict import predictor

app = FastAPI(
    title="Air Quality Monitoring – Anomaly Detection API",
    description="Real-time IoT Air Quality Streaming, ETL, and MLOps Anomaly Detection Service.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Enable CORS for Streamlit dashboard and web clients
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Operational metrics counters
SERVER_START_TIME = time.time()
PREDICTION_COUNTER = 0


# Pydantic Schemas
class LocationSchema(BaseModel):
    lat: float = Field(..., ge=-90.0, le=90.0, example=48.8566)
    lon: float = Field(..., ge=-180.0, le=180.0, example=2.3522)


class MeasurementsSchema(BaseModel):
    pm2_5: float = Field(..., ge=0.0, le=500.0, example=12.5, description="Particulate Matter 2.5 in µg/m³")
    pm10: float = Field(..., ge=0.0, le=600.0, example=25.3, description="Particulate Matter 10 in µg/m³")
    no2: float = Field(..., ge=0.0, le=400.0, example=40.2, description="Nitrogen Dioxide in µg/m³")
    o3: float = Field(..., ge=0.0, le=500.0, example=80.1, description="Ozone in µg/m³")
    temperature: float = Field(..., ge=-25.0, le=60.0, example=22.5, description="Temperature in °C")
    humidity: float = Field(..., ge=0.0, le=100.0, example=65.0, description="Relative Humidity in %")


class SensorTelemetryRequest(BaseModel):
    sensor_id: str = Field(..., example="CAP_001")
    timestamp: str = Field(..., example="2026-11-15T14:30:00Z")
    location: LocationSchema
    measurements: MeasurementsSchema
    status: Optional[str] = Field("active", example="active")


class PredictionResponse(BaseModel):
    sensor_id: str
    timestamp: str
    prediction_label: int
    prediction_status: str
    anomaly_probability: float
    is_anomaly: bool
    latency_ms: float
    model_version: str


# Endpoints
@app.get("/health", tags=["Monitoring"])
def get_health() -> Dict[str, Any]:
    """Returns platform operational health, uptime, and database status."""
    uptime = time.time() - SERVER_START_TIME
    return {
        "status": "HEALTHY",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "uptime_seconds": round(uptime, 1),
        "database_backend": db.backend_type,
        "model_loaded": predictor.model is not None,
        "model_version": predictor.model_version,
        "total_predictions_served": PREDICTION_COUNTER
    }


@app.post("/predict", response_model=PredictionResponse, tags=["Inference"])
def predict_anomaly(payload: SensorTelemetryRequest) -> PredictionResponse:
    """
    Evaluates real-time sensor reading and returns anomaly classification.
    """
    global PREDICTION_COUNTER
    try:
        data_dict = payload.model_dump()
        result = predictor.predict_single(data_dict)

        # Record prediction into database for lineage and auditability
        db.save_prediction(result)
        PREDICTION_COUNTER += 1

        return PredictionResponse(**result)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Inference error: {str(e)}"
        )


@app.get("/anomalies", tags=["Data"])
def get_anomalies(
    limit: int = Query(50, ge=1, le=500),
    severity: Optional[str] = Query(None, description="Filter by severity: LOW, MEDIUM, HIGH, CRITICAL")
) -> List[Dict[str, Any]]:
    """Returns list of detected anomalies from database."""
    anomalies = db.get_anomalies(limit=limit)
    if severity:
        anomalies = [a for a in anomalies if a.get("severity") == severity.upper()]
    return anomalies


@app.get("/measurements", tags=["Data"])
def get_measurements(
    sensor_id: Optional[str] = Query(None, description="Optional sensor filter"),
    limit: int = Query(100, ge=1, le=1000)
) -> List[Dict[str, Any]]:
    """Returns latest sensor measurements."""
    return db.get_recent_measurements(sensor_id=sensor_id, limit=limit)


@app.get("/catalog", tags=["DataOps"])
def get_data_catalog() -> List[Dict[str, Any]]:
    """Returns data lineage and freshness catalog."""
    return db.get_catalog_lineage()


@app.get("/metrics", tags=["DataOps"])
def get_operational_metrics() -> Dict[str, Any]:
    """Returns DataOps telemetry metrics."""
    return {
        "predictions_total": PREDICTION_COUNTER,
        "database_backend": db.backend_type,
        "uptime_seconds": round(time.time() - SERVER_START_TIME, 2),
        "current_timestamp": datetime.now(timezone.utc).isoformat()
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api.main:app", host="0.0.0.0", port=8000, reload=False)
