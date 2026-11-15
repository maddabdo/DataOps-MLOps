# Live Demonstration Scenario for Academic Defense (20 Minutes)
## Air Quality Monitoring – Real-Time Anomaly Detection Platform

**Master:** Intelligence Artificielle Embarquée (MIAE)  
**Module:** DataOps & MLOps | **Academic Year:** 2026–2027  
**Professor Evaluator:** Prof. Yasmine LAMARI (`y.lamari@uiz.ac.ma`)  
**Target Duration:** 20 minutes (12 min presentation & demo, 8 min Q&A)

---

### Step 1: System Health & Infrastructure Boot (2 minutes)
1. **Show Docker Services:**
   ```bash
   docker compose ps
   ```
   *Demonstrate that Kafka, Zookeeper, PostgreSQL, MLflow, FastAPI, and Streamlit are healthy.*
2. **Show Health Endpoint:**
   - Open browser at `http://localhost:8000/health`
   - Point out: `status: HEALTHY`, `database_backend: postgresql`, `model_loaded: true`.

---

### Step 2: Data Ingestion & Streaming (3 minutes)
1. **Explain the IoT Simulation:**
   - Show `ingestion/sensor_generator.py`: circadian curves for NO2 and O3, sinusoidal temperature/humidity, and multi-station geographical coordinates (Paris urban context).
2. **Execute Ingestion to Kafka:**
   ```bash
   python ingestion/kafka_producer.py
   ```
3. **Inspect Kafka UI:**
   - Open `http://localhost:8085`
   - Show the 3 created topics: `raw_data`, `processed_data`, `anomalies`.
   - Inspect a recent JSON payload in `raw_data` partition.

---

### Step 3: Spark Streaming & Data Cleaning (3 minutes)
1. **Data Cleaning Rules:**
   - Show `processing/data_cleaning.py`: boundary clipping (PM2.5 [0, 500], NO2 [0, 400]), missing value imputation, deduplication cache `(sensor_id, timestamp)`.
2. **Business Anomaly Engine:**
   - Show `processing/anomaly_rules.py`: European Union Directive & WHO standards:
     - PM2.5 > 50 µg/m³ (Alert), > 80 µg/m³ (Critical)
     - PM10 > 100 µg/m³
     - NO2 > 200 µg/m³ (Traffic Smog)
     - O3 > 180 µg/m³ (Summer Ozone)
     - Delta spikes > 40 µg/m³

---

### Step 4: Machine Learning Lifecycle & MLflow (4 minutes)
1. **Model Training & Comparison:**
   - Explain the leak-free chronological split (80% train / 20% test).
   - Compare Random Forest vs. Gradient Boosting.
2. **Show MLflow Tracking Dashboard:**
   - Open `http://localhost:5000`
   - Show experiment `air_quality_anomaly_detection`.
   - Show tracked hyperparameters (learning rate, estimators), metrics (Accuracy: 98.3%, Precision: 100%, F1: 87.2%, ROC-AUC: 99.7%).
   - Show confusion matrix artifact.
   - Show Model Registry: version transitioned from `Staging` to `Production`.

---

### Step 5: Real-Time API Inference (3 minutes)
1. **Interactive Swagger Documentation:**
   - Open `http://localhost:8000/docs`
2. **Live POST `/predict` Execution:**
   - Submit a test payload with normal values -> Returns `prediction_status: "Normal"`, `is_anomaly: false`, latency ~ 2ms.
   - Submit an anomalous payload with PM2.5 = 75.0 µg/m³ -> Returns `prediction_status: "Anomaly"`, `anomaly_probability: 0.98`, `is_anomaly: true`.

---

### Step 6: Interactive Dashboard & Anomaly Injection (5 minutes)
1. **Open Streamlit Dashboard:**
   - Open `http://localhost:8501`
2. **Walkthrough Tabs:**
   - **Tab 1: Telemetry Charts:** Point out real-time PM2.5/PM10 curves against the WHO red threshold line.
   - **Tab 2: Anomaly Log:** Show detected alarms with severity tags (`CRITICAL`, `HIGH`).
   - **Tab 3: Sensor Map:** Show GPS station markers on the interactive map.
   - **Tab 4: Prediction Lab:** Let the professor drag the PM2.5 / NO2 sliders and click **"Run Inference"** to see live predictions.
   - **Tab 5: Data Lineage Catalog:** Show data completeness metrics and lineage provenance (satisfying Academic Phase 4).
3. **Live Anomaly Injection Demonstration:**
   - In the sidebar, click the red button **"⚠️ Inject Anomaly"**.
   - Notice the metric card instantly refresh, active anomaly counter increment, and alert banner trigger!

---

### Step 7: Q&A and Academic Wrap-up
- Answer questions on Airflow DAG branching, backfilling, MLflow registry transitions, and DataOps observability.
