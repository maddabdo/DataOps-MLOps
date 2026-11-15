#!/usr/bin/env python3
"""
Data Cleaning, Schema Validation, and Preprocessing
Air Quality Monitoring – Real-Time Anomaly Detection Platform

Implements:
- Schema validation
- Physical range boundary verification
- Missing value imputation
- Deduplication handling
- Quality scoring
"""

from datetime import datetime
from typing import Dict, Any, Tuple, Optional, List


# Physical validity bounds for outdoor air quality sensors
PHYSICAL_BOUNDS = {
    "pm2_5": (0.0, 500.0),       # µg/m³
    "pm10": (0.0, 600.0),        # µg/m³
    "no2": (0.0, 400.0),         # µg/m³
    "o3": (0.0, 500.0),          # µg/m³
    "temperature": (-25.0, 55.0),# °C
    "humidity": (0.0, 100.0)     # %
}

REQUIRED_KEYS = ["sensor_id", "timestamp", "location", "measurements", "status"]
REQUIRED_MEASUREMENT_KEYS = ["pm2_5", "pm10", "no2", "o3", "temperature", "humidity"]


class DataCleaner:
    """
    Cleans, validates, and normalizes incoming air quality sensor records.
    """

    def __init__(self, bounds: Optional[Dict[str, Tuple[float, float]]] = None):
        self.bounds = bounds or PHYSICAL_BOUNDS
        self.seen_records = set()  # Deduplication cache (sensor_id, timestamp)
        self.max_cache_size = 10000

    def validate_schema(self, payload: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
        """Checks presence and format of required top-level keys."""
        if not isinstance(payload, dict):
            return False, "Payload is not a dictionary"

        for k in REQUIRED_KEYS:
            if k not in payload:
                return False, f"Missing top-level key: {k}"

        loc = payload.get("location")
        if not isinstance(loc, dict) or "lat" not in loc or "lon" not in loc:
            return False, "Invalid location structure"

        meas = payload.get("measurements")
        if not isinstance(meas, dict):
            return False, "Missing or non-dict measurements field"

        for mk in REQUIRED_MEASUREMENT_KEYS:
            if mk not in meas:
                return False, f"Missing measurement key: {mk}"

        # Timestamp validation
        try:
            ts_str = payload["timestamp"].replace("Z", "+00:00")
            datetime.fromisoformat(ts_str)
        except Exception:
            return False, f"Invalid ISO 8601 timestamp: {payload['timestamp']}"

        return True, None

    def check_and_deduplicate(self, payload: Dict[str, Any]) -> bool:
        """
        Returns True if the record is unique, False if duplicate.
        """
        key = (payload["sensor_id"], payload["timestamp"])
        if key in self.seen_records:
            return False
        if len(self.seen_records) >= self.max_cache_size:
            self.seen_records.clear()
        self.seen_records.add(key)
        return True

    def clean_record(self, payload: Dict[str, Any]) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """
        Validates, sanitizes measurements, and calculates data quality metrics.
        Returns:
            (cleaned_payload, quality_report)
        """
        is_valid_schema, schema_err = self.validate_schema(payload)
        if not is_valid_schema:
            return payload, {
                "is_clean": False,
                "error": schema_err,
                "sanitized_fields": []
            }

        is_unique = self.check_and_deduplicate(payload)
        cleaned = {
            "sensor_id": payload["sensor_id"],
            "timestamp": payload["timestamp"],
            "location": payload["location"],
            "measurements": {},
            "status": payload.get("status", "active")
        }

        sanitized_fields = []
        meas = payload["measurements"]

        for field, (min_val, max_val) in self.bounds.items():
            raw_val = meas.get(field)
            if raw_val is None or not isinstance(raw_val, (int, float)):
                # Default fallback imputation
                val = 0.0
                sanitized_fields.append((field, "missing_imputed", val))
            elif raw_val < min_val:
                val = min_val
                sanitized_fields.append((field, "below_min_clipped", raw_val))
            elif raw_val > max_val:
                val = max_val
                sanitized_fields.append((field, "above_max_clipped", raw_val))
            else:
                val = float(raw_val)

            cleaned["measurements"][field] = round(val, 2)

        quality_report = {
            "is_clean": len(sanitized_fields) == 0 and is_unique,
            "is_duplicate": not is_unique,
            "sanitized_fields": sanitized_fields,
            "completeness_score": 1.0 - (len(sanitized_fields) / len(self.bounds))
        }

        return cleaned, quality_report


if __name__ == "__main__":
    cleaner = DataCleaner()
    sample = {
        "sensor_id": "CAP_001",
        "timestamp": "2026-11-15T14:30:00Z",
        "location": {"lat": 48.8566, "lon": 2.3522},
        "measurements": {
            "pm2_5": 12.5,
            "pm10": 25.3,
            "no2": -50.0,  # Negative test value
            "o3": 80.1,
            "temperature": 22.5,
            "humidity": 65
        },
        "status": "active"
    }
    cleaned_data, report = cleaner.clean_record(sample)
    print("Cleaned Data:", cleaned_data)
    print("Quality Report:", report)
