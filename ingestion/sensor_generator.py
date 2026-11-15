#!/usr/bin/env python3
"""
IoT Air Quality Sensor Simulator
Air Quality Monitoring – Real-Time Anomaly Detection Platform

Generates realistic sensor telemetry adhering to the OpenAQ / Academic specification:
- Circadian patterns (rush-hour NO2/PM, solar peak O3, temperature/humidity cycles)
- Controlled anomaly injection (spikes, industrial pollution, stuck sensors)
- JSON serialization ready for Kafka streaming or batch file export
"""

import json
import math
import random
import time
from datetime import datetime, timezone
from typing import Dict, List, Optional, Generator, Any


class SensorStation:
    """Represents a physical air quality monitoring station."""
    def __init__(
        self,
        sensor_id: str,
        name: str,
        lat: float,
        lon: float,
        station_type: str = "urban"
    ):
        self.sensor_id = sensor_id
        self.name = name
        self.lat = lat
        self.lon = lon
        self.station_type = station_type
        self.last_measurements: Optional[Dict[str, float]] = None


# Realistic monitoring locations (Paris / European urban context from academic spec)
DEFAULT_STATIONS = [
    SensorStation("CAP_001", "Station Chatelet - Paris Centre", 48.8566, 2.3522, "traffic"),
    SensorStation("CAP_002", "Station Bastille - Paris Est", 48.8530, 2.3698, "urban"),
    SensorStation("CAP_003", "Station Montparnasse - Paris Sud", 48.8421, 2.3219, "traffic"),
    SensorStation("CAP_004", "Station Bois de Boulogne", 48.8624, 2.2492, "background"),
    SensorStation("CAP_005", "Station Zone Industrielle Nord", 48.9102, 2.3855, "industrial")
]


class AirQualitySensorGenerator:
    """
    Simulates high-fidelity telemetry from air quality IoT sensor stations.
    """

    def __init__(
        self,
        stations: Optional[List[SensorStation]] = None,
        anomaly_probability: float = 0.05,
        random_seed: Optional[int] = 42
    ):
        self.stations = stations or DEFAULT_STATIONS
        self.anomaly_probability = anomaly_probability
        if random_seed is not None:
            random.seed(random_seed)

    def _calculate_baseline_values(self, hour: float, station_type: str) -> Dict[str, float]:
        """
        Calculates physically realistic baseline values using circadian cycles.
        """
        # Solar / temperature cycle peaking at 15:00 (3 PM)
        temp_cycle = math.sin(math.pi * (hour - 9) / 12)
        base_temp = 18.0 + 8.0 * temp_cycle + random.gauss(0, 0.8)

        # Humidity is inversely correlated with temperature
        base_humidity = max(20.0, min(95.0, 75.0 - 25.0 * temp_cycle + random.gauss(0, 2.0)))

        # Traffic rush hour curve (peaks around 8h and 18h)
        morning_rush = math.exp(-((hour - 8.0) ** 2) / 3.0)
        evening_rush = math.exp(-((hour - 18.0) ** 2) / 4.0)
        traffic_factor = morning_rush + evening_rush

        # Station multiplier
        type_mult = 1.4 if station_type == "traffic" else (1.8 if station_type == "industrial" else 0.7)

        # Pollutant baselines (µg/m³)
        pm2_5 = max(2.0, (12.0 + 15.0 * traffic_factor * type_mult) + random.gauss(0, 2.5))
        pm10 = max(5.0, (pm2_5 * 1.8 + 10.0 * traffic_factor) + random.gauss(0, 4.0))
        no2 = max(5.0, (25.0 + 35.0 * traffic_factor * type_mult) + random.gauss(0, 3.5))

        # Ozone (O3) forms via photochemical reactions in sunlight, peaking 14h-16h
        sunlight = max(0.0, math.sin(math.pi * (hour - 6) / 14)) if 6 <= hour <= 20 else 0.0
        o3 = max(5.0, (20.0 + 60.0 * sunlight) + random.gauss(0, 4.0))

        return {
            "pm2_5": round(pm2_5, 2),
            "pm10": round(pm10, 2),
            "no2": round(no2, 2),
            "o3": round(o3, 2),
            "temperature": round(base_temp, 1),
            "humidity": round(base_humidity, 1)
        }

    def _inject_anomaly(self, measurements: Dict[str, float]) -> tuple[Dict[str, float], str]:
        """
        Injects realistic anomaly patterns:
        1. Heavy particulate spike (industrial puff or construction)
        2. Toxic NO2 rush hour surge
        3. Extreme ozone photochemical smog
        4. Sensor malfunction / stuck flatline or negative readings
        """
        anomaly_kind = random.choice([
            "pm_spike",
            "traffic_smog",
            "ozone_surge",
            "sensor_fault"
        ])

        m = measurements.copy()
        if anomaly_kind == "pm_spike":
            # Significant PM exceedance over European Union alert threshold (PM10 > 100, PM2.5 > 50)
            m["pm2_5"] = round(m["pm2_5"] + random.uniform(55.0, 180.0), 2)
            m["pm10"] = round(m["pm10"] + random.uniform(90.0, 300.0), 2)
        elif anomaly_kind == "traffic_smog":
            # High NO2 exceedance (> 200 µg/m³)
            m["no2"] = round(m["no2"] + random.uniform(150.0, 280.0), 2)
            m["pm10"] = round(m["pm10"] + random.uniform(40.0, 80.0), 2)
        elif anomaly_kind == "ozone_surge":
            # High summer Ozone episode (> 180 µg/m³ alert threshold)
            m["o3"] = round(m["o3"] + random.uniform(120.0, 210.0), 2)
            m["temperature"] = round(m["temperature"] + random.uniform(5.0, 10.0), 1)
        elif anomaly_kind == "sensor_fault":
            # Sensor calibration error or aberrant outlier
            fault_type = random.choice(["flatline", "extreme_negative", "saturation"])
            if fault_type == "flatline":
                m["pm2_5"] = 0.0
                m["pm10"] = 0.0
            elif fault_type == "extreme_negative":
                m["no2"] = -999.0
            else:
                m["pm2_5"] = 999.9

        return m, anomaly_kind

    def generate_single_reading(
        self,
        station: Optional[SensorStation] = None,
        dt: Optional[datetime] = None,
        force_anomaly: bool = False
    ) -> Dict[str, Any]:
        """
        Generates a single IoT measurement payload adhering to the specification.
        """
        station = station or random.choice(self.stations)
        now_dt = dt or datetime.now(timezone.utc)
        hour = now_dt.hour + now_dt.minute / 60.0

        measurements = self._calculate_baseline_values(hour, station.station_type)
        is_anomaly = force_anomaly or (random.random() < self.anomaly_probability)
        anomaly_type = None

        if is_anomaly:
            measurements, anomaly_type = self._inject_anomaly(measurements)

        payload = {
            "sensor_id": station.sensor_id,
            "timestamp": now_dt.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "location": {
                "lat": station.lat,
                "lon": station.lon
            },
            "measurements": measurements,
            "status": "active" if anomaly_type != "sensor_fault" else "warning"
        }
        station.last_measurements = measurements
        return payload

    def stream_readings(
        self,
        interval_seconds: float = 1.0,
        limit: Optional[int] = None
    ) -> Generator[Dict[str, Any], None, None]:
        """
        Infinite or bounded generator for streaming simulated sensor messages.
        """
        count = 0
        while True:
            for station in self.stations:
                yield self.generate_single_reading(station)
                count += 1
                if limit and count >= limit:
                    return
            time.sleep(interval_seconds)

    def generate_batch(
        self,
        n_samples: int = 1000,
        start_date: Optional[datetime] = None,
        step_minutes: int = 15
    ) -> List[Dict[str, Any]]:
        """
        Generates historical batch data for training ML models or backfilling.
        """
        from datetime import timedelta
        current_dt = start_date or datetime(2026, 11, 1, 0, 0, tzinfo=timezone.utc)
        records = []
        for _ in range(n_samples):
            station = random.choice(self.stations)
            records.append(self.generate_single_reading(station, dt=current_dt))
            current_dt += timedelta(minutes=step_minutes)
        return records


if __name__ == "__main__":
    generator = AirQualitySensorGenerator()
    sample = generator.generate_single_reading()
    print("Simulated Single Reading:")
    print(json.dumps(sample, indent=2))
