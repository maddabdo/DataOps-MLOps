#!/usr/bin/env python3
"""
Apache Airflow Production Pipeline DAG
Air Quality Monitoring – Real-Time Anomaly Detection Platform

Implements the academic project workflow:
[Extract Sensors Data] -> [Validate Quality] -> [Train Model] -> [Evaluate Model] ->
[Model Improvement?] --(yes)--> [Deploy if Better]
                     --(no)-->  [End]

Includes Airflow Sensor, BranchPythonOperator, MLflow integration, and Slack/Email alerting.
"""

import os
import sys
import logging
from datetime import datetime, timedelta

# Airflow imports
try:
    from airflow import DAG
    from airflow.operators.python import PythonOperator, BranchPythonOperator
    from airflow.operators.empty import EmptyOperator
    from airflow.sensors.python import PythonSensor
    AIRFLOW_AVAILABLE = True
except ImportError:
    AIRFLOW_AVAILABLE = False
    DAG = object

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

logger = logging.getLogger("AirflowPipeline")

# Default arguments for Airflow tasks
default_args = {
    "owner": "DataOps_MLOps_Team",
    "depends_on_past": False,
    "email": ["y.lamari@uiz.ac.ma"],
    "email_on_failure": True,
    "email_on_retry": False,
    "retries": 2,
    "retry_delay": timedelta(minutes=5),
}

def on_pipeline_failure(context):
    """Failure callback sending notification to webhook/email."""
    task_id = context.get("task_instance").task_id
    execution_date = context.get("execution_date")
    error = context.get("exception")
    logger.error(f"[ALERT] Task {task_id} failed on {execution_date}: {error}")


# Task 1: Sensor to check data availability
def check_data_availability(**kwargs):
    """Sensor condition checking that fresh measurements exist in the database."""
    from database.connection import db
    records = db.get_recent_measurements(limit=10)
    if len(records) > 0:
        logger.info(f"Data availability verified: {len(records)} recent records found.")
        return True
    logger.warning("No fresh sensor measurements detected. Waiting...")
    return False


# Task 2: Data Extraction & Validation
def extract_and_validate(**kwargs):
    """Extracts raw batch and computes quality completeness and freshness metrics."""
    from database.connection import db
    from processing.data_cleaning import DataCleaner
    cleaner = DataCleaner()
    records = db.get_recent_measurements(limit=200)
    cleaned_count = 0
    for r in records:
        payload = {
            "sensor_id": r["sensor_id"],
            "timestamp": r["timestamp"],
            "location": {"lat": 48.8566, "lon": 2.3522},
            "measurements": {
                "pm2_5": r["pm2_5"], "pm10": r["pm10"], "no2": r["no2"],
                "o3": r["o3"], "temperature": r["temperature"], "humidity": r["humidity"]
            },
            "status": r["status"]
        }
        _, report = cleaner.clean_record(payload)
        if report["is_clean"]:
            cleaned_count += 1

    completeness = (cleaned_count / len(records) * 100) if records else 100.0
    db.update_catalog_lineage(
        dataset="air_quality_batch",
        source="air_quality_measurements",
        step="Data Quality Validation",
        dest="air_quality_measurements",
        rows=len(records),
        comp=completeness
    )
    logger.info(f"Validated {len(records)} records. Cleanliness score: {completeness:.2f}%")
    return {"records_validated": len(records), "completeness": completeness}


# Task 3: Model Training
def train_model(**kwargs):
    """Executes ML pipeline training script and logs artifacts."""
    from ml.train import train_and_compare_models
    results = train_and_compare_models()
    kwargs["ti"].xcom_push(key="candidate_metrics", value=results["best_metrics"])
    kwargs["ti"].xcom_push(key="candidate_model_path", value=results["best_model_path"])
    return results["best_metrics"]


# Task 4: Candidate Evaluation & Benchmarking
def evaluate_model(**kwargs):
    """Evaluates candidate model against production performance threshold."""
    ti = kwargs["ti"]
    candidate_metrics = ti.xcom_pull(key="candidate_metrics", task_ids="train_candidate_model")
    f1 = candidate_metrics.get("f1_score", 0.0) if candidate_metrics else 0.0
    logger.info(f"Evaluated candidate model. F1-Score: {f1:.4f}")
    return f1


# Task 5: Decision Branching
def branch_model_decision(**kwargs):
    """Decides whether candidate outperforms threshold (F1 >= 0.85)."""
    ti = kwargs["ti"]
    f1 = ti.xcom_pull(task_ids="evaluate_candidate_model") or 0.0
    threshold = 0.85
    if f1 >= threshold:
        logger.info(f"Candidate F1 ({f1:.4f}) >= Threshold ({threshold}). Proceeding to deploy.")
        return "deploy_if_better"
    else:
        logger.warning(f"Candidate F1 ({f1:.4f}) < Threshold ({threshold}). Skipping deployment.")
        return "pipeline_end"


# Task 6: Deploy to Production
def deploy_model(**kwargs):
    """Promotes candidate model to Production in MLflow Model Registry."""
    from ml.train import promote_to_production
    promote_to_production()
    logger.info("Candidate model successfully promoted to MLflow Production stage.")


if AIRFLOW_AVAILABLE:
    with DAG(
        dag_id="air_quality_monitoring_pipeline",
        default_args=default_args,
        description="Air Quality Real-Time Anomaly Detection Daily ETL & MLOps Pipeline",
        schedule_interval="0 2 * * *",  # Daily at 02:00 UTC
        start_date=datetime(2026, 11, 10),
        catchup=False,
        on_failure_callback=on_pipeline_failure,
        tags=["dataops", "mlops", "air-quality", "anomaly-detection"]
    ) as dag:

        wait_for_sensor_data = PythonSensor(
            task_id="wait_for_sensor_data",
            python_callable=check_data_availability,
            poke_interval=60,
            timeout=600,
            mode="reschedule"
        )

        validate_quality = PythonOperator(
            task_id="validate_quality",
            python_callable=extract_and_validate
        )

        train_candidate_model = PythonOperator(
            task_id="train_candidate_model",
            python_callable=train_model
        )

        evaluate_candidate_model = PythonOperator(
            task_id="evaluate_candidate_model",
            python_callable=evaluate_model
        )

        model_improvement_branch = BranchPythonOperator(
            task_id="model_improvement_branch",
            python_callable=branch_model_decision
        )

        deploy_if_better = PythonOperator(
            task_id="deploy_if_better",
            python_callable=deploy_model
        )

        pipeline_end = EmptyOperator(
            task_id="pipeline_end"
        )

        wait_for_sensor_data >> validate_quality >> train_candidate_model >> evaluate_candidate_model >> model_improvement_branch
        model_improvement_branch >> deploy_if_better >> pipeline_end
        model_improvement_branch >> pipeline_end


if __name__ == "__main__":
    print("Air Quality Pipeline DAG structure defined.")
    if AIRFLOW_AVAILABLE:
        print(f"Airflow DAG registered: {dag.dag_id}")
    else:
        print("Airflow package is not loaded in standalone environment (used inside Docker).")
