#!/usr/bin/env python3
"""
Apache Airflow Historical Backfill DAG
Air Quality Monitoring – Real-Time Anomaly Detection Platform

Allows re-executing historical ETL, metric calculation, and anomaly detection
across past date ranges without impacting the primary daily production schedule.
"""

import os
import sys
import logging
from datetime import datetime, timedelta

try:
    from airflow import DAG
    from airflow.operators.python import PythonOperator
    from airflow.operators.empty import EmptyOperator
    AIRFLOW_AVAILABLE = True
except ImportError:
    AIRFLOW_AVAILABLE = False
    DAG = object

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

logger = logging.getLogger("AirflowBackfill")

default_args = {
    "owner": "DataOps_MLOps_Team",
    "depends_on_past": False,
    "email": ["y.lamari@uiz.ac.ma"],
    "email_on_failure": True,
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
}

def execute_historical_backfill(**kwargs):
    """Generates and processes historical sensor data for backfilled interval."""
    from ingestion.sensor_generator import AirQualitySensorGenerator
    from database.connection import db
    from processing.spark_streaming import SparkStreamProcessor

    execution_date = kwargs.get("execution_date", datetime.now())
    logger.info(f"Starting historical backfill for execution date: {execution_date}")

    generator = AirQualitySensorGenerator()
    processor = SparkStreamProcessor()

    # Generate historical slice of 50 samples
    historical_samples = generator.generate_batch(n_samples=50, start_date=execution_date)
    processed_count = 0
    anomaly_count = 0

    for sample in historical_samples:
        res = processor.process_message(sample)
        meas_id = db.save_measurement(res["processed_record"])
        if res["has_anomaly"]:
            for a in res["anomalies"]:
                db.save_anomaly(a, measurement_id=meas_id)
                anomaly_count += 1
        processed_count += 1

    db.update_catalog_lineage(
        dataset="historical_backfill",
        source="IoT Generator Batch",
        step="Historical Backfill Ingestion",
        dest="air_quality_measurements",
        rows=processed_count,
        comp=100.0
    )
    logger.info(f"Backfill complete for {execution_date}: {processed_count} measurements, {anomaly_count} anomalies.")


if AIRFLOW_AVAILABLE:
    with DAG(
        dag_id="air_quality_historical_backfill",
        default_args=default_args,
        description="Air Quality Historical Data Backfill DAG",
        schedule_interval=None,  # Triggered manually with execution_date parameter
        start_date=datetime(2026, 11, 1),
        catchup=False,
        tags=["dataops", "backfill", "air-quality"]
    ) as backfill_dag:

        start_backfill = EmptyOperator(task_id="start_backfill")
        run_backfill = PythonOperator(
            task_id="run_historical_backfill",
            python_callable=execute_historical_backfill
        )
        end_backfill = EmptyOperator(task_id="end_backfill")

        start_backfill >> run_backfill >> end_backfill


if __name__ == "__main__":
    print("Air Quality Historical Backfill DAG defined.")
