#!/usr/bin/env python3
"""
Business Rule Anomaly Detection Engine
Air Quality Monitoring – Real-Time Anomaly Detection Platform

Implements rule-based heuristics derived from:
- WHO Air Quality Guidelines (2021)
- European Union Directive 2008/50/EC on ambient air quality
- Rate-of-change delta spike detection
- Sensor flatline / stuck readings
"""

from typing import Dict, Any, List, Optional


# Official Alert & Information Thresholds (µg/m³)
THRESHOLDS = {
    "pm2_5_who_daily": 15.0,        # WHO recommended 24h level
    "pm2_5_alert": 50.0,            # High pollution alert
    "pm2_5_critical": 80.0,         # Critical emergency
    "pm10_alert": 100.0,            # EU alert threshold
    "pm10_critical": 150.0,
    "no2_hourly_alert": 200.0,      # EU 1-hour alert threshold
    "no2_critical": 300.0,
    "o3_info_threshold": 180.0,     # EU public information threshold
    "o3_alert_threshold": 240.0,    # EU alert threshold
    "delta_pm2_5_spike": 40.0       # Sudden delta spike between readings
}


class AnomalyRulesEngine:
    """
    Evaluates real-time sensor measurements against expert business rules.
    """

    def __init__(self, thresholds: Optional[Dict[str, float]] = None):
        self.thresholds = thresholds or THRESHOLDS
        self.previous_readings: Dict[str, Dict[str, float]] = {}

    def evaluate(self, payload: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Inspects measurements and returns a list of triggered anomaly events.
        """
        anomalies = []
        sensor_id = payload.get("sensor_id", "UNKNOWN")
        timestamp = payload.get("timestamp", "")
        meas = payload.get("measurements", {})

        pm2_5 = meas.get("pm2_5", 0.0)
        pm10 = meas.get("pm10", 0.0)
        no2 = meas.get("no2", 0.0)
        o3 = meas.get("o3", 0.0)

        # Rule 1: PM2.5 Exceedance
        if pm2_5 >= self.thresholds["pm2_5_critical"]:
            anomalies.append({
                "sensor_id": sensor_id,
                "timestamp": timestamp,
                "anomaly_type": "PM2_5_CRITICAL_EXCEEDANCE",
                "severity": "CRITICAL",
                "rule_triggered": f"PM2.5 ({pm2_5} µg/m³) >= {self.thresholds['pm2_5_critical']}",
                "value_observed": pm2_5,
                "threshold": self.thresholds["pm2_5_critical"]
            })
        elif pm2_5 >= self.thresholds["pm2_5_alert"]:
            anomalies.append({
                "sensor_id": sensor_id,
                "timestamp": timestamp,
                "anomaly_type": "PM2_5_HIGH_POLLUTION",
                "severity": "HIGH",
                "rule_triggered": f"PM2.5 ({pm2_5} µg/m³) >= {self.thresholds['pm2_5_alert']}",
                "value_observed": pm2_5,
                "threshold": self.thresholds["pm2_5_alert"]
            })

        # Rule 2: PM10 Exceedance
        if pm10 >= self.thresholds["pm10_critical"]:
            anomalies.append({
                "sensor_id": sensor_id,
                "timestamp": timestamp,
                "anomaly_type": "PM10_CRITICAL_EXCEEDANCE",
                "severity": "CRITICAL",
                "rule_triggered": f"PM10 ({pm10} µg/m³) >= {self.thresholds['pm10_critical']}",
                "value_observed": pm10,
                "threshold": self.thresholds["pm10_critical"]
            })
        elif pm10 >= self.thresholds["pm10_alert"]:
            anomalies.append({
                "sensor_id": sensor_id,
                "timestamp": timestamp,
                "anomaly_type": "PM10_ALERT",
                "severity": "HIGH",
                "rule_triggered": f"PM10 ({pm10} µg/m³) >= {self.thresholds['pm10_alert']}",
                "value_observed": pm10,
                "threshold": self.thresholds["pm10_alert"]
            })

        # Rule 3: NO2 Exceedance (Traffic Smog)
        if no2 >= self.thresholds["no2_critical"]:
            anomalies.append({
                "sensor_id": sensor_id,
                "timestamp": timestamp,
                "anomaly_type": "NO2_CRITICAL_SMOG",
                "severity": "CRITICAL",
                "rule_triggered": f"NO2 ({no2} µg/m³) >= {self.thresholds['no2_critical']}",
                "value_observed": no2,
                "threshold": self.thresholds["no2_critical"]
            })
        elif no2 >= self.thresholds["no2_hourly_alert"]:
            anomalies.append({
                "sensor_id": sensor_id,
                "timestamp": timestamp,
                "anomaly_type": "NO2_HOURLY_ALERT",
                "severity": "HIGH",
                "rule_triggered": f"NO2 ({no2} µg/m³) >= {self.thresholds['no2_hourly_alert']}",
                "value_observed": no2,
                "threshold": self.thresholds["no2_hourly_alert"]
            })

        # Rule 4: Ozone (O3) Summer Peak
        if o3 >= self.thresholds["o3_alert_threshold"]:
            anomalies.append({
                "sensor_id": sensor_id,
                "timestamp": timestamp,
                "anomaly_type": "O3_ALERT_THRESHOLD",
                "severity": "CRITICAL",
                "rule_triggered": f"O3 ({o3} µg/m³) >= {self.thresholds['o3_alert_threshold']}",
                "value_observed": o3,
                "threshold": self.thresholds["o3_alert_threshold"]
            })
        elif o3 >= self.thresholds["o3_info_threshold"]:
            anomalies.append({
                "sensor_id": sensor_id,
                "timestamp": timestamp,
                "anomaly_type": "O3_INFORMATION_THRESHOLD",
                "severity": "MEDIUM",
                "rule_triggered": f"O3 ({o3} µg/m³) >= {self.thresholds['o3_info_threshold']}",
                "value_observed": o3,
                "threshold": self.thresholds["o3_info_threshold"]
            })

        # Rule 5: Delta Spike Detection
        if sensor_id in self.previous_readings:
            prev_pm2_5 = self.previous_readings[sensor_id].get("pm2_5", 0.0)
            delta = abs(pm2_5 - prev_pm2_5)
            if delta >= self.thresholds["delta_pm2_5_spike"]:
                anomalies.append({
                    "sensor_id": sensor_id,
                    "timestamp": timestamp,
                    "anomaly_type": "PM2_5_DELTA_SPIKE",
                    "severity": "MEDIUM",
                    "rule_triggered": f"Delta PM2.5 ({delta:.1f} µg/m³) >= {self.thresholds['delta_pm2_5_spike']}",
                    "value_observed": delta,
                    "threshold": self.thresholds["delta_pm2_5_spike"]
                })

        self.previous_readings[sensor_id] = meas
        return anomalies


if __name__ == "__main__":
    engine = AnomalyRulesEngine()
    test_reading = {
        "sensor_id": "CAP_001",
        "timestamp": "2026-11-15T15:00:00Z",
        "measurements": {
            "pm2_5": 78.5,
            "pm10": 110.0,
            "no2": 45.0,
            "o3": 60.0
        }
    }
    detected = engine.evaluate(test_reading)
    print(f"Detected {len(detected)} anomalies:")
    for a in detected:
        print(f" - [{a['severity']}] {a['anomaly_type']}: {a['rule_triggered']}")
