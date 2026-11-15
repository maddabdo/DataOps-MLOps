-- ==============================================================================
-- Schema DDL: Air Quality Monitoring - Real-Time Anomaly Detection Platform
-- ==============================================================================

-- 1. Sensor metadata
CREATE TABLE IF NOT EXISTS sensors (
    sensor_id VARCHAR(50) PRIMARY KEY,
    name VARCHAR(150) NOT NULL,
    location_lat DOUBLE PRECISION NOT NULL,
    location_lon DOUBLE PRECISION NOT NULL,
    station_type VARCHAR(50) DEFAULT 'urban',
    status VARCHAR(50) DEFAULT 'active',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 2. Cleaned and validated air quality measurements
CREATE TABLE IF NOT EXISTS air_quality_measurements (
    id SERIAL PRIMARY KEY,
    sensor_id VARCHAR(50) NOT NULL REFERENCES sensors(sensor_id) ON DELETE CASCADE,
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
    pm2_5 DOUBLE PRECISION NOT NULL,
    pm10 DOUBLE PRECISION NOT NULL,
    no2 DOUBLE PRECISION NOT NULL,
    o3 DOUBLE PRECISION NOT NULL,
    temperature DOUBLE PRECISION NOT NULL,
    humidity DOUBLE PRECISION NOT NULL,
    status VARCHAR(50) DEFAULT 'active',
    is_clean BOOLEAN DEFAULT TRUE,
    completeness_score DOUBLE PRECISION DEFAULT 1.0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT unique_sensor_measurement UNIQUE (sensor_id, timestamp)
);

CREATE INDEX IF NOT EXISTS idx_measurements_sensor_ts ON air_quality_measurements(sensor_id, timestamp);
CREATE INDEX IF NOT EXISTS idx_measurements_timestamp ON air_quality_measurements(timestamp);

-- 3. Detected business rule anomaly events
CREATE TABLE IF NOT EXISTS anomalies (
    id SERIAL PRIMARY KEY,
    measurement_id INTEGER REFERENCES air_quality_measurements(id) ON DELETE SET NULL,
    sensor_id VARCHAR(50) NOT NULL REFERENCES sensors(sensor_id) ON DELETE CASCADE,
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
    anomaly_type VARCHAR(100) NOT NULL,
    severity VARCHAR(20) NOT NULL CHECK (severity IN ('LOW', 'MEDIUM', 'HIGH', 'CRITICAL')),
    rule_triggered TEXT NOT NULL,
    value_observed DOUBLE PRECISION NOT NULL,
    threshold DOUBLE PRECISION NOT NULL,
    is_resolved BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_anomalies_severity ON anomalies(severity);
CREATE INDEX IF NOT EXISTS idx_anomalies_timestamp ON anomalies(timestamp);

-- 4. Machine learning model predictions
CREATE TABLE IF NOT EXISTS model_predictions (
    id SERIAL PRIMARY KEY,
    model_name VARCHAR(100) NOT NULL,
    model_version VARCHAR(50) NOT NULL,
    sensor_id VARCHAR(50) NOT NULL REFERENCES sensors(sensor_id) ON DELETE CASCADE,
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
    prediction_label INTEGER NOT NULL,          -- 0: Normal, 1: Anomaly
    anomaly_probability DOUBLE PRECISION NOT NULL,
    is_anomaly BOOLEAN NOT NULL,
    actual_label INTEGER,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_predictions_model ON model_predictions(model_name, model_version);
CREATE INDEX IF NOT EXISTS idx_predictions_timestamp ON model_predictions(timestamp);

-- 5. Data Catalog & Data Lineage (Academic Phase 4 Deliverable)
CREATE TABLE IF NOT EXISTS data_lineage_catalog (
    id SERIAL PRIMARY KEY,
    dataset_name VARCHAR(100) NOT NULL,
    source_type VARCHAR(50) NOT NULL,            -- e.g. 'IoT Simulator', 'Kafka Topic'
    transformation_step VARCHAR(100) NOT NULL,   -- e.g. 'Spark Streaming Cleaning'
    destination_table VARCHAR(100) NOT NULL,
    freshness_timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    row_count INTEGER DEFAULT 0,
    completeness_pct DOUBLE PRECISION DEFAULT 100.0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Seed Initial Default Sensor Stations
INSERT INTO sensors (sensor_id, name, location_lat, location_lon, station_type, status)
VALUES
    ('CAP_001', 'Station Chatelet - Paris Centre', 48.8566, 2.3522, 'traffic', 'active'),
    ('CAP_002', 'Station Bastille - Paris Est', 48.8530, 2.3698, 'urban', 'active'),
    ('CAP_003', 'Station Montparnasse - Paris Sud', 48.8421, 2.3219, 'traffic', 'active'),
    ('CAP_004', 'Station Bois de Boulogne', 48.8624, 2.2492, 'background', 'active'),
    ('CAP_005', 'Station Zone Industrielle Nord', 48.9102, 2.3855, 'industrial', 'active')
ON CONFLICT (sensor_id) DO NOTHING;
