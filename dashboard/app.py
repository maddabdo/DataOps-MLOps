#!/usr/bin/env python3
"""
Interactive Real-Time Monitoring & DataOps Dashboard
Air Quality Monitoring – Real-Time Anomaly Detection Platform

Streamlit web application for professor live demonstration:
1. Real-Time Telemetry Gauges (PM2.5, PM10, NO2, O3, Temp, Humidity)
2. Interactive Time-Series Charts with WHO Alert Limits
3. Anomaly Tracking Table & Severity Breakdown
4. Live Sensor Geographic Map
5. Real-Time Interactive Prediction & Anomaly Injector
6. DataOps Pipeline Quality & Data Lineage Catalog
"""

import os
import sys
import time
from datetime import datetime, timezone
import streamlit as st
import pandas as pd

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from database.connection import db
from ingestion.sensor_generator import AirQualitySensorGenerator, DEFAULT_STATIONS
from processing.anomaly_rules import AnomalyRulesEngine
from ml.predict import predictor

st.set_page_config(
    page_title="Air Quality Monitoring – DataOps & MLOps",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Header
st.title("🌍 Air Quality Monitoring – Real-Time Anomaly Detection Platform")
st.caption("Master: Intelligence Artificielle Embarquée (MIAE) | Module: DataOps & MLOps | Academic Year: 2026–2027")

# Sidebar Controls
st.sidebar.header("🕹️ Station & Stream Controls")
selected_station_id = st.sidebar.selectbox(
    "Select Monitoring Station:",
    options=["ALL"] + [s.sensor_id for s in DEFAULT_STATIONS],
    index=0
)

# Simulation Injector in Sidebar
st.sidebar.markdown("---")
st.sidebar.subheader("🧪 Live Professor Demonstration")
col_sim1, col_sim2 = st.sidebar.columns(2)
with col_sim1:
    if st.button("📥 Generate Normal"):
        gen = AirQualitySensorGenerator()
        reading = gen.generate_single_reading(force_anomaly=False)
        meas_id = db.save_measurement(reading)
        st.sidebar.success(f"Generated normal reading #{meas_id}")
with col_sim2:
    if st.button("⚠️ Inject Anomaly"):
        gen = AirQualitySensorGenerator()
        reading = gen.generate_single_reading(force_anomaly=True)
        meas_id = db.save_measurement(reading)
        anom_engine = AnomalyRulesEngine()
        anomalies = anom_engine.evaluate(reading)
        for a in anomalies:
            db.save_anomaly(a, measurement_id=meas_id)
        st.sidebar.error(f"Injected {len(anomalies)} anomalies!")

# Fetch Data
measurements = db.get_recent_measurements(
    sensor_id=None if selected_station_id == "ALL" else selected_station_id,
    limit=100
)
anomalies = db.get_anomalies(limit=50)

# If database is fresh, populate a seed batch
if len(measurements) == 0:
    gen = AirQualitySensorGenerator()
    seed_batch = gen.generate_batch(n_samples=25)
    for s in seed_batch:
        m_id = db.save_measurement(s)
        anoms = AnomalyRulesEngine().evaluate(s)
        for a in anoms:
            db.save_anomaly(a, measurement_id=m_id)
    measurements = db.get_recent_measurements(limit=100)
    anomalies = db.get_anomalies(limit=50)

df_meas = pd.DataFrame(measurements)
if not df_meas.empty and "timestamp" in df_meas.columns:
    df_meas["timestamp"] = pd.to_datetime(df_meas["timestamp"])
    df_meas = df_meas.sort_values("timestamp")

# Top Metrics Row
st.markdown("### 📊 Current Environmental Indicators")
m1, m2, m3, m4, m5, m6 = st.columns(6)

latest = df_meas.iloc[-1] if not df_meas.empty else None

def get_metric_delta(val, threshold):
    if val >= threshold:
        return f"+{val - threshold:.1f} (EXCEEDANCE)"
    return f"{val - threshold:.1f} (OK)"

if latest is not None:
    m1.metric("PM 2.5", f"{latest['pm2_5']} µg/m³", delta=get_metric_delta(latest['pm2_5'], 50.0), delta_color="inverse")
    m2.metric("PM 10", f"{latest['pm10']} µg/m³", delta=get_metric_delta(latest['pm10'], 100.0), delta_color="inverse")
    m3.metric("NO₂", f"{latest['no2']} µg/m³", delta=get_metric_delta(latest['no2'], 200.0), delta_color="inverse")
    m4.metric("Ozone (O₃)", f"{latest['o3']} µg/m³", delta=get_metric_delta(latest['o3'], 180.0), delta_color="inverse")
    m5.metric("Temperature", f"{latest['temperature']} °C")
    m6.metric("Active Anomalies", f"{len(anomalies)}", delta="Critical Alerts" if len(anomalies) > 0 else "Normal", delta_color="inverse")

# Main Tabs
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📈 Time Series Telemetry",
    "🚨 Detected Anomalies",
    "🗺️ Sensor Network Map",
    "🤖 MLOps Prediction Lab",
    "📦 DataOps & Lineage Catalog"
])

with tab1:
    st.subheader("Real-Time Telemetry & Environmental Thresholds")
    if not df_meas.empty:
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("**Particulate Matter: PM 2.5 & PM 10 (WHO / EU Limit: 50 / 100 µg/m³)**")
            st.line_chart(df_meas.set_index("timestamp")[["pm2_5", "pm10"]])
        with c2:
            st.markdown("**Gaseous Pollutants: Nitrogen Dioxide (NO₂) & Ozone (O₃)**")
            st.line_chart(df_meas.set_index("timestamp")[["no2", "o3"]])

        st.markdown("**Meteorological Conditions: Temperature (°C) & Humidity (%)**")
        st.line_chart(df_meas.set_index("timestamp")[["temperature", "humidity"]])
    else:
        st.info("No sensor measurements recorded yet.")

with tab2:
    st.subheader("Real-Time Anomaly Detection Log")
    if anomalies:
        df_anom = pd.DataFrame(anomalies)
        st.dataframe(
            df_anom[["id", "sensor_id", "timestamp", "anomaly_type", "severity", "value_observed", "threshold", "rule_triggered"]],
            use_container_width=True
        )
    else:
        st.success("✅ No anomalies detected in current monitoring stream.")

with tab3:
    st.subheader("Geographic Sensor Station Map")
    stations_data = []
    for s in DEFAULT_STATIONS:
        stations_data.append({
            "sensor_id": s.sensor_id,
            "name": s.name,
            "lat": s.lat,
            "lon": s.lon,
            "station_type": s.station_type
        })
    df_stations = pd.DataFrame(stations_data)
    st.map(df_stations, latitude="lat", longitude="lon", zoom=11)
    st.dataframe(df_stations, use_container_width=True)

with tab4:
    st.subheader("MLOps Real-Time Prediction Playground")
    st.markdown("Test the production classification model on custom sensor inputs:")
    p_col1, p_col2 = st.columns(2)
    with p_col1:
        test_pm25 = st.slider("PM 2.5 (µg/m³)", 0.0, 200.0, 18.0)
        test_pm10 = st.slider("PM 10 (µg/m³)", 0.0, 300.0, 35.0)
        test_no2 = st.slider("NO₂ (µg/m³)", 0.0, 300.0, 42.0)
    with p_col2:
        test_o3 = st.slider("Ozone O₃ (µg/m³)", 0.0, 250.0, 45.0)
        test_temp = st.slider("Temperature (°C)", -10.0, 45.0, 21.0)
        test_hum = st.slider("Humidity (%)", 10.0, 100.0, 65.0)

    if st.button("🔮 Run Inference on Production Model"):
        input_payload = {
            "sensor_id": "TEST_STATION",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "location": {"lat": 48.8566, "lon": 2.3522},
            "measurements": {
                "pm2_5": test_pm25, "pm10": test_pm10, "no2": test_no2,
                "o3": test_o3, "temperature": test_temp, "humidity": test_hum
            },
            "status": "active"
        }
        res = predictor.predict_single(input_payload)
        if res["is_anomaly"]:
            st.error(f"🚨 **ANOMALY DETECTED!** Probability: {res['anomaly_probability']*100:.1f}% (Inference Latency: {res['latency_ms']} ms)")
        else:
            st.success(f"✅ **NORMAL QUALITY AIR.** Probability: {res['anomaly_probability']*100:.1f}% (Inference Latency: {res['latency_ms']} ms)")
        st.json(res)

with tab5:
    st.subheader("DataOps Metadata Catalog & Data Lineage (Academic Phase 4)")
    st.markdown("Automated metadata tracking ensuring end-to-end data provenance and quality completeness:")
    catalog_entries = db.get_catalog_lineage()
    if catalog_entries:
        st.dataframe(pd.DataFrame(catalog_entries), use_container_width=True)
    else:
        st.info("Lineage catalog will display after initial pipeline execution.")

st.markdown("---")
st.caption("Air Quality Monitoring Platform | Developed for Academic Project Evaluation | December 2026")
