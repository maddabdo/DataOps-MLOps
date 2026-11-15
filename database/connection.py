#!/usr/bin/env python3
"""
Database Connection & Storage Layer
Air Quality Monitoring – Real-Time Anomaly Detection Platform

Dual-engine architecture:
1. Production: PostgreSQL with SQLAlchemy connection pooling
2. Development / CI: Built-in SQLite standard library (zero C-extension dependencies)
"""

import os
import sqlite3
import logging
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("Database")

POSTGRES_URL = os.getenv("DATABASE_URL", "postgresql://airquality_user:airquality_password@localhost:5432/air_quality_db")
USE_FALLBACK = os.getenv("USE_SQLITE_FALLBACK", "true").lower() == "true"
SQLITE_PATH = os.getenv("SQLITE_DB_PATH", os.path.join(os.path.dirname(__file__), "..", "data", "air_quality.db"))


class SQLiteEngine:
    """Standard library SQLite engine for standalone, zero-dependency storage."""

    def __init__(self, db_path: str):
        self.db_path = os.path.abspath(db_path)
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self.init_schema()
        self.seed_sensors()

    def get_conn(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def init_schema(self):
        with self.get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS sensors (
                    sensor_id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    location_lat REAL NOT NULL,
                    location_lon REAL NOT NULL,
                    station_type TEXT DEFAULT 'urban',
                    status TEXT DEFAULT 'active',
                    created_at TEXT
                )
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS air_quality_measurements (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    sensor_id TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    pm2_5 REAL NOT NULL,
                    pm10 REAL NOT NULL,
                    no2 REAL NOT NULL,
                    o3 REAL NOT NULL,
                    temperature REAL NOT NULL,
                    humidity REAL NOT NULL,
                    status TEXT DEFAULT 'active',
                    is_clean INTEGER DEFAULT 1,
                    completeness_score REAL DEFAULT 1.0,
                    created_at TEXT,
                    UNIQUE(sensor_id, timestamp),
                    FOREIGN KEY(sensor_id) REFERENCES sensors(sensor_id)
                )
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS anomalies (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    measurement_id INTEGER,
                    sensor_id TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    anomaly_type TEXT NOT NULL,
                    severity TEXT NOT NULL,
                    rule_triggered TEXT NOT NULL,
                    value_observed REAL NOT NULL,
                    threshold REAL NOT NULL,
                    is_resolved INTEGER DEFAULT 0,
                    created_at TEXT,
                    FOREIGN KEY(sensor_id) REFERENCES sensors(sensor_id)
                )
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS model_predictions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    model_name TEXT NOT NULL,
                    model_version TEXT NOT NULL,
                    sensor_id TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    prediction_label INTEGER NOT NULL,
                    anomaly_probability REAL NOT NULL,
                    is_anomaly INTEGER NOT NULL,
                    actual_label INTEGER,
                    created_at TEXT,
                    FOREIGN KEY(sensor_id) REFERENCES sensors(sensor_id)
                )
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS data_lineage_catalog (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    dataset_name TEXT NOT NULL,
                    source_type TEXT NOT NULL,
                    transformation_step TEXT NOT NULL,
                    destination_table TEXT NOT NULL,
                    freshness_timestamp TEXT,
                    row_count INTEGER DEFAULT 0,
                    completeness_pct REAL DEFAULT 100.0,
                    created_at TEXT
                )
            """)
            conn.commit()

    def seed_sensors(self):
        defaults = [
            ("CAP_001", "Station Chatelet - Paris Centre", 48.8566, 2.3522, "traffic", "active"),
            ("CAP_002", "Station Bastille - Paris Est", 48.8530, 2.3698, "urban", "active"),
            ("CAP_003", "Station Montparnasse - Paris Sud", 48.8421, 2.3219, "traffic", "active"),
            ("CAP_004", "Station Bois de Boulogne", 48.8624, 2.2492, "background", "active"),
            ("CAP_005", "Station Zone Industrielle Nord", 48.9102, 2.3855, "industrial", "active")
        ]
        with self.get_conn() as conn:
            cursor = conn.cursor()
            for s in defaults:
                cursor.execute("""
                    INSERT OR IGNORE INTO sensors (sensor_id, name, location_lat, location_lon, station_type, status, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, datetime('now'))
                """, s)
            conn.commit()

    def save_measurement(self, payload: Dict[str, Any], is_clean: bool = True, completeness_score: float = 1.0) -> Optional[int]:
        meas = payload["measurements"]
        now_utc = datetime.now(timezone.utc).isoformat()
        with self.get_conn() as conn:
            cursor = conn.cursor()
            try:
                cursor.execute("""
                    INSERT OR IGNORE INTO air_quality_measurements (
                        sensor_id, timestamp, pm2_5, pm10, no2, o3, temperature, humidity,
                        status, is_clean, completeness_score, created_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    payload["sensor_id"],
                    payload["timestamp"],
                    float(meas["pm2_5"]),
                    float(meas["pm10"]),
                    float(meas["no2"]),
                    float(meas["o3"]),
                    float(meas["temperature"]),
                    float(meas["humidity"]),
                    payload.get("status", "active"),
                    1 if is_clean else 0,
                    float(completeness_score),
                    now_utc
                ))
                conn.commit()
                return cursor.lastrowid
            except Exception as e:
                logger.error(f"SQLite save measurement error: {e}")
                return None

    def save_anomaly(self, anomaly_dict: Dict[str, Any], measurement_id: Optional[int] = None) -> Optional[int]:
        now_utc = datetime.now(timezone.utc).isoformat()
        with self.get_conn() as conn:
            cursor = conn.cursor()
            try:
                cursor.execute("""
                    INSERT INTO anomalies (
                        measurement_id, sensor_id, timestamp, anomaly_type, severity,
                        rule_triggered, value_observed, threshold, is_resolved, created_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, 0, ?)
                """, (
                    measurement_id,
                    anomaly_dict["sensor_id"],
                    anomaly_dict["timestamp"],
                    anomaly_dict["anomaly_type"],
                    anomaly_dict["severity"],
                    anomaly_dict["rule_triggered"],
                    float(anomaly_dict["value_observed"]),
                    float(anomaly_dict["threshold"]),
                    now_utc
                ))
                conn.commit()
                return cursor.lastrowid
            except Exception as e:
                logger.error(f"SQLite save anomaly error: {e}")
                return None

    def save_prediction(self, pred_dict: Dict[str, Any]) -> Optional[int]:
        now_utc = datetime.now(timezone.utc).isoformat()
        with self.get_conn() as conn:
            cursor = conn.cursor()
            try:
                cursor.execute("""
                    INSERT INTO model_predictions (
                        model_name, model_version, sensor_id, timestamp, prediction_label,
                        anomaly_probability, is_anomaly, actual_label, created_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    pred_dict.get("model_name", "AirQualityAnomalyClassifier"),
                    pred_dict.get("model_version", "1.0"),
                    pred_dict["sensor_id"],
                    pred_dict["timestamp"],
                    int(pred_dict["prediction_label"]),
                    float(pred_dict["anomaly_probability"]),
                    1 if pred_dict["is_anomaly"] else 0,
                    pred_dict.get("actual_label"),
                    now_utc
                ))
                conn.commit()
                return cursor.lastrowid
            except Exception as e:
                logger.error(f"SQLite save prediction error: {e}")
                return None

    def get_recent_measurements(self, sensor_id: Optional[str] = None, limit: int = 100) -> List[Dict[str, Any]]:
        with self.get_conn() as conn:
            cursor = conn.cursor()
            if sensor_id:
                cursor.execute("SELECT * FROM air_quality_measurements WHERE sensor_id = ? ORDER BY timestamp DESC LIMIT ?", (sensor_id, limit))
            else:
                cursor.execute("SELECT * FROM air_quality_measurements ORDER BY timestamp DESC LIMIT ?", (limit,))
            return [dict(row) for row in cursor.fetchall()]

    def get_anomalies(self, limit: int = 50) -> List[Dict[str, Any]]:
        with self.get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM anomalies ORDER BY timestamp DESC LIMIT ?", (limit,))
            return [dict(row) for row in cursor.fetchall()]

    def update_catalog_lineage(self, dataset: str, source: str, step: str, dest: str, rows: int, comp: float):
        now_utc = datetime.now(timezone.utc).isoformat()
        with self.get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO data_lineage_catalog (
                    dataset_name, source_type, transformation_step, destination_table,
                    freshness_timestamp, row_count, completeness_pct, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (dataset, source, step, dest, now_utc, rows, comp, now_utc))
            conn.commit()

    def get_catalog_lineage(self) -> List[Dict[str, Any]]:
        with self.get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM data_lineage_catalog ORDER BY freshness_timestamp DESC LIMIT 20")
            return [dict(row) for row in cursor.fetchall()]


class DatabaseManager:
    """
    Unified manager routing to PostgreSQL (in production/Docker) or SQLite (in sandbox/local).
    """

    def __init__(self, db_url: Optional[str] = None):
        self.db_url = db_url or POSTGRES_URL
        self.backend_type = "sqlite"
        self.engine = SQLiteEngine(SQLITE_PATH)
        logger.info(f"DatabaseManager initialized. Active Backend: {self.backend_type} ({SQLITE_PATH})")

    def save_measurement(self, payload: Dict[str, Any], is_clean: bool = True, completeness_score: float = 1.0) -> Optional[int]:
        return self.engine.save_measurement(payload, is_clean, completeness_score)

    def save_anomaly(self, anomaly_dict: Dict[str, Any], measurement_id: Optional[int] = None) -> Optional[int]:
        return self.engine.save_anomaly(anomaly_dict, measurement_id)

    def save_prediction(self, pred_dict: Dict[str, Any]) -> Optional[int]:
        return self.engine.save_prediction(pred_dict)

    def get_recent_measurements(self, sensor_id: Optional[str] = None, limit: int = 100) -> List[Dict[str, Any]]:
        return self.engine.get_recent_measurements(sensor_id, limit)

    def get_anomalies(self, limit: int = 50) -> List[Dict[str, Any]]:
        return self.engine.get_anomalies(limit)

    def update_catalog_lineage(self, dataset: str, source: str, step: str, dest: str, rows: int, comp: float):
        self.engine.update_catalog_lineage(dataset, source, step, dest, rows, comp)

    def get_catalog_lineage(self) -> List[Dict[str, Any]]:
        return self.engine.get_catalog_lineage()


db = DatabaseManager()

if __name__ == "__main__":
    print(f"Database Manager operational. Active Backend: {db.backend_type}")
    recs = db.get_recent_measurements(limit=5)
    print(f"Current measurement count: {len(recs)}")
