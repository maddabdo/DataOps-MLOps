# Air Quality Monitoring – Real-Time Anomaly Detection Platform
### Master Intelligence Artificielle Embarquée (MIAE) – Module DataOps & MLOps
**Academic Year:** 2026–2027 | **Evaluator:** Prof. Yasmine LAMARI (`y.lamari@uiz.ac.ma`)

---

## Slide 1: Project Identity & Team Organization
- **Project Title:** Plateforme de Détection d'Anomalies en Temps Réel pour la Qualité de l'Air
- **Context:** Inspired by OpenAQ worldwide environmental monitoring networks.
- **Team Size:** 3 Members
  - **Member 1 (DevOps & Project Lead):** Scrum Master, Apache Kafka, Apache Airflow, Docker Infrastructure.
  - **Member 2 (Data Engineer):** Python Streaming, Spark ETL, Data Validation, PostgreSQL Database.
  - **Member 3 (MLOps Engineer):** Machine Learning, MLflow Tracking & Registry, FastAPI, Streamlit Dashboard.
- **Agile Methodology:** 5 Jira Sprints (10 Nov – 15 Dec 2026), 7 Epics, 17 Stories, 43 automated unit tests.

---

## Slide 2: Problem Statement & Industrial Objectives
- **Problem:** Urban air pollution (fine particulate matter PM2.5/PM10, toxic NO2, summer ozone O3) has severe public health impacts. IoT sensors produce continuous high-velocity data streams prone to missing values, drift, and unexpected pollution spikes.
- **Objectives:**
  1. Real-time streaming ingestion from heterogeneous IoT stations.
  2. Automatic cleaning, deduplication, and domain rule evaluation (WHO 2021 & EU Directive 2008/50/EC).
  3. Relational persistence with data lineage tracking.
  4. Scheduled automated retraining and conditional model deployment via Apache Airflow.
  5. Full ML lifecycle tracking and version control with MLflow.
  6. Sub-50ms REST API prediction endpoints.
  7. Interactive supervision dashboard for real-time alerts.

---

## Slide 3: Global System Architecture
- **Layer 1: Ingestion:** IoT Telemetry Simulator ➔ Apache Kafka (`raw_data` topic).
- **Layer 2: Processing:** Spark Streaming / Python ETL ➔ Cleaning & Deduplication ➔ Anomaly Rules Engine ➔ Split into `processed_data` & `anomalies`.
- **Layer 3: Storage:** PostgreSQL 16 (Relational schema for sensors, measurements, anomalies, predictions, data lineage).
- **Layer 4: Orchestration:** Apache Airflow DAGs with PythonSensor, BranchPythonOperator, and backfilling.
- **Layer 5: MLOps:** MLflow Tracking Server + MLflow Model Registry (Staging ➔ Production promotion).
- **Layer 6: Serving & Monitoring:** FastAPI REST API (Swagger/OpenAPI) + Streamlit Interactive Dashboard.

---

## Slide 4: Phase 1 – Ingestion & Kafka Streaming
- **Realistic Telemetry Generator:**
  - Circadian sinusoidal cycles for temperature and humidity.
  - Morning (8h) and evening (18h) rush-hour traffic curves for NO2 and PM10.
  - Photochemical solar curves for Ozone (O3) peaking 14h–16h.
  - Anomaly injector: particulate spikes, traffic smog, ozone surges, sensor flatlines.
- **Kafka Multi-Topic Architecture:**
  - `raw_data`: High-velocity raw JSON incoming messages.
  - `processed_data`: Cleaned, validated, and quality-scored records.
  - `anomalies`: Critical exceedance alerts for immediate emergency response.
  - Fast socket probing and resilient fallback buffer for high availability.

---

## Slide 5: Phase 2 – Streaming ETL, Cleaning & Business Rules
- **Data Validation & Sanitization:**
  - Physical boundary checks (PM2.5: [0, 500], NO2: [0, 400], Temp: [-25, 55]).
  - Automated clipping and missing value imputation.
  - In-memory cache deduplication keyed on `(sensor_id, timestamp)`.
- **Domain Anomaly Rules Engine:**
  - **PM2.5:** Alert at $\ge 50\,\mu\text{g/m}^3$; Critical at $\ge 80\,\mu\text{g/m}^3$.
  - **PM10:** Alert at $\ge 100\,\mu\text{g/m}^3$; Critical at $\ge 150\,\mu\text{g/m}^3$.
  - **NO2:** 1-hour smog alert at $\ge 200\,\mu\text{g/m}^3$; Critical at $\ge 300\,\mu\text{g/m}^3$.
  - **O3:** Public info threshold at $\ge 180\,\mu\text{g/m}^3$; Alert at $\ge 240\,\mu\text{g/m}^3$.
  - **Delta Spikes:** Rapid jump $> 40\,\mu\text{g/m}^3$ between consecutive station readings.

---

## Slide 6: Phase 2 – Apache Airflow Orchestration
- **Daily Production Workflow (`air_quality_pipeline`):**
  - `wait_for_sensor_data` (PythonSensor): Pokes database to confirm fresh streaming data availability.
  - `validate_quality` (PythonOperator): Calculates data cleanliness and completeness scores.
  - `train_candidate_model` (PythonOperator): Executes model training and outputs candidate metrics.
  - `evaluate_candidate_model` (PythonOperator): Benchmarks candidate performance against baseline.
  - `model_improvement_branch` (BranchPythonOperator): Decision logic:
    - If candidate $F_1 \ge 0.85$ ➔ Branch to `deploy_if_better`.
    - Else ➔ Branch to `pipeline_end` (preserves current production model).
  - `deploy_if_better`: Promotes candidate to `Production` stage in MLflow Model Registry.
- **Historical Backfill Workflow (`air_quality_backfill`):**
  - Parameterized execution_date for reprocessing past historical intervals.
- **Alerting:** Automated `on_failure_callback` for email/webhook alerting.

---

## Slide 7: Phase 3 – Machine Learning & Feature Engineering
- **Domain-Specific Feature Engineering:**
  - Raw pollutant readings: PM2.5, PM10, NO2, O3, Temperature, Humidity.
  - Interaction ratios: $PM_{\text{ratio}} = \frac{PM_{2.5}}{PM_{10} + 10^{-5}}$ (distinguishes combustion soot from dust).
  - Traffic proxy: $\frac{NO_2 \times PM_{10}}{1000}$.
  - Harmonic circadian encodings: $\sin\left(\frac{2\pi \cdot \text{hour}}{24}\right)$ and $\cos\left(\frac{2\pi \cdot \text{hour}}{24}\right)$.
- **Zero-Data-Leakage Protocol:**
  - Strict **chronological time-series split** (80% training / 20% testing).
  - Normalization scaler fitted **strictly on training partition**, transforming test partition.

---

## Slide 8: Phase 3 – Model Comparison & Experimental Results
- **Algorithm Comparison:**
  - **Random Forest Classifier:** Ensemble bagging with balanced class weights.
  - **Gradient Boosting Classifier:** Sequential boosting minimizing log-loss.

| Metric | Random Forest | Gradient Boosting (Selected Best) |
| :--- | :--- | :--- |
| **Accuracy** | 94.67% | **98.33%** |
| **Precision** | **100.00%** | **100.00%** |
| **Recall** | 27.27% | **77.27%** |
| **F1-Score** | 0.4286 | **0.8718** |
| **ROC-AUC** | 0.9969 | **0.9974** |

- **Conclusion:** Gradient Boosting demonstrated superior recall and balanced F1-score ($0.8718$), reliably catching non-linear multi-pollutant combinations with zero false alarms.

---

## Slide 9: Phase 3 – MLflow Tracking & Model Registry
- **Experiment Tracking:**
  - Tracks all training runs under `air_quality_anomaly_detection`.
  - Automatically logs hyperparameters, accuracy, precision, recall, F1, and ROC-AUC.
  - Logs confusion matrix JSON/image artifacts.
- **Model Registry Lifecycle:**
  - Automatic versioning of candidate models.
  - Stage transitions: `None` ➔ `Staging` ➔ `Production`.
  - Archived legacy versions automatically upon candidate promotion.
  - Decouples training pipeline from real-time API consumers.

---

## Slide 10: Phase 4 – FastAPI Microservice Serving
- **Architecture & Performance:**
  - Asynchronous FastAPI framework with OpenAPI / Swagger interactive documentation at `/docs`.
  - Pydantic models enforcing physical data validation before inference.
  - Sub-millisecond inference latency ($< 3\,\text{ms}$ per request).
- **Core Endpoints:**
  - `GET /health`: Platform health, uptime, database backend, model version.
  - `POST /predict`: Real-time anomaly classification with probability score.
  - `GET /anomalies`: Filterable query of detected anomalies by severity.
  - `GET /measurements`: Query historical sensor records.
  - `GET /catalog`: DataOps lineage and quality metadata.
  - `GET /metrics`: Operational throughput counters.

---

## Slide 11: Phase 4 – Interactive Streamlit Dashboard
- **Professor Live Demonstration Features:**
  - **Top KPI Cards:** Instant delta indicators for PM2.5, PM10, NO2, O3 against WHO standards.
  - **Time Series Tab:** Interactive pollutant curves with threshold overlay.
  - **Anomaly Log Tab:** Real-time event log with severity filtering (`CRITICAL`, `HIGH`).
  - **Geographic Map Tab:** Interactive GPS station markers across Parisian monitoring stations.
  - **Prediction Lab Tab:** Slider controls allowing manual parameter adjustments and instant inference.
  - **Live Injection Button:** 1-click sidebar button to inject an emergency anomaly spike during presentation.

---

## Slide 12: Phase 4 – DataOps Metadata & Lineage Catalog
- **Addressing Academic Phase 4 Requirement:**
  - Lightweight data catalog tracking data provenance and end-to-end lineage.
  - Ingests dataset source (`IoT Generator`), transformation step (`Spark Streaming Cleaning`), and destination table (`air_quality_measurements`).
  - Records data completeness percentages and freshness timestamps.
  - Exposed via `GET /catalog` and rendered in the Streamlit DataOps tab.

---

## Slide 13: Quality Assurance, Testing & CI/CD
- **Automated Test Suite:**
  - **43 comprehensive unit, integration, and end-to-end tests** executed via pytest.
  - `test_sensor_generator.py` (5 tests): Schema compliance and physical bounds.
  - `test_data_cleaning.py` (5 tests): Validation, clipping, and deduplication.
  - `test_anomaly_rules.py` (6 tests): Thresholds, alerts, and delta spikes.
  - `test_database.py` (5 tests): Relational CRUD and SQLite/Postgres fallback.
  - `test_spark_streaming.py` (3 tests): Streaming micro-batch processing.
  - `test_kafka_integration.py` (3 tests): Producer buffering and consumer subscriptions.
  - `test_airflow_pipeline.py` (3 tests): Sensors, operators, and branching logic.
  - `test_ml_pipeline.py` (5 tests): Feature extraction, training, and predictor.
  - `test_api.py` (7 tests): All FastAPI REST endpoints and validation errors.
  - `test_end_to_end.py` (1 test): Complete data lifecycle from generator to API.
- **Pass Rate:** **100% (43 / 43 Passed in 8.58 seconds)**.

---

## Slide 14: Docker Compose Infrastructure
- **Containerized Multi-Service Topology:**
  - `aqm-zookeeper`: Confluent Zookeeper 7.5.0
  - `aqm-kafka`: Confluent Kafka Broker with auto-topic creation
  - `aqm-kafka-ui`: Web UI for topic and consumer inspection (Port 8085)
  - `aqm-postgres`: PostgreSQL 16 Alpine with persistent volume and schema DDL
  - `aqm-mlflow`: MLflow Tracking Server with artifact storage (Port 5000)
  - `aqm-api`: FastAPI production microservice (Port 8000)
  - `aqm-dashboard`: Streamlit real-time dashboard (Port 8501)
  - `aqm-sensor-generator`: Background telemetry publishing service
- **Health Checks & Auto-Healing:** Inter-service dependencies managed via `condition: service_healthy`.

---

## Slide 15: Limitations & Future Perspectives
- **Current Limitations:**
  - Simulated IoT sensors instead of physical hardware transceivers (LoRaWAN/MQTT).
  - Anomaly labels generated via rule-augmented heuristics rather than ground-truth clinical data.
- **Perspectives & Improvements:**
  - Ingest real OpenAQ global live APIs via Kafka Connect.
  - Deploy Apache Kafka and Airflow on Kubernetes using Helm charts.
  - Integrate Edge AI (TensorFlow Lite / ONNX Runtime) directly on embedded microcontrollers (ESP32/Raspberry Pi) matching the MIAE master curriculum.

---

## Slide 16: Conclusion & Academic Summary
- **Accomplishments:**
  - Fully implemented, containerized, and documented DataOps & MLOps platform delivered 30 days ahead of the 15 December 2026 deadline.
  - Complete integration of streaming (Kafka/Spark), storage (PostgreSQL), orchestration (Airflow), ML lifecycle (MLflow), serving (FastAPI), and visualization (Streamlit).
  - 43/43 automated tests passing.
  - Complete LaTeX report and Jira Scrum project backlog delivered.
- **Thank you for your attention! Questions & Live Demonstration.**
