#!/usr/bin/env python3
"""
Custom Airflow MLflow Operator
Air Quality Monitoring – Real-Time Anomaly Detection Platform

Custom operator to track experiments, log parameters, metrics, and register models
directly from Apache Airflow tasks into MLflow.
"""

import logging
from typing import Dict, Any, Optional

try:
    from airflow.models.baseoperator import BaseOperator
    from airflow.utils.decorators import apply_defaults
except ImportError:
    BaseOperator = object
    def apply_defaults(f):
        return f

logger = logging.getLogger("MLflowOperator")


class MLflowModelEvaluationOperator(BaseOperator):
    """
    Airflow Operator that evaluates a candidate model against an evaluation threshold.
    """

    @apply_defaults
    def __init__(
        self,
        experiment_name: str,
        metric_name: str = "f1_score",
        min_threshold: float = 0.85,
        *args, **kwargs
    ):
        super(MLflowModelEvaluationOperator, self).__init__(*args, **kwargs)
        self.experiment_name = experiment_name
        self.metric_name = metric_name
        self.min_threshold = min_threshold

    def execute(self, context: Dict[str, Any]) -> bool:
        logger.info(f"Evaluating model in experiment '{self.experiment_name}' on metric '{self.metric_name}'")
        # Pull candidate metrics from XCom
        ti = context["ti"]
        candidate_metrics = ti.xcom_pull(key="candidate_metrics") or {}
        score = candidate_metrics.get(self.metric_name, 0.0)

        passed = score >= self.min_threshold
        logger.info(f"Score: {score:.4f} (Threshold: {self.min_threshold}) -> Passed: {passed}")
        return passed
