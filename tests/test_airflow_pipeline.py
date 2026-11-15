"""
Unit Tests: Airflow DAG Structure & Task Callables
Air Quality Monitoring – Real-Time Anomaly Detection Platform
"""

import pytest
from airflow.dags.air_quality_pipeline import (
    check_data_availability, extract_and_validate, branch_model_decision
)


def test_airflow_sensor_check():
    # After database initialization, check_data_availability should return boolean
    result = check_data_availability()
    assert isinstance(result, bool)


def test_airflow_extract_and_validate():
    report = extract_and_validate()
    assert "records_validated" in report
    assert "completeness" in report
    assert report["completeness"] >= 0.0


def test_branch_model_decision_mock():
    class DummyTaskInstance:
        def xcom_pull(self, **kwargs):
            return 0.92

    class DummyContext:
        def get(self, key):
            return None

    res = branch_model_decision(ti=DummyTaskInstance())
    assert res == "deploy_if_better"

    class LowF1TaskInstance:
        def xcom_pull(self, **kwargs):
            return 0.65

    res_low = branch_model_decision(ti=LowF1TaskInstance())
    assert res_low == "pipeline_end"
