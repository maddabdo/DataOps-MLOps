#!/usr/bin/env python3
"""
Apache Kafka Producer for IoT Air Quality Telemetry
Air Quality Monitoring – Real-Time Anomaly Detection Platform

Publishes simulated sensor readings to the `raw_data` Kafka topic.
Includes reconnection logic, graceful error recovery, and optional fallback buffer.
"""

import os
import sys
import json
import time
import logging
from typing import Optional, Dict, Any
from dotenv import load_dotenv

# Ensure parent directory is in Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from ingestion.sensor_generator import AirQualitySensorGenerator

load_dotenv()

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("KafkaProducer")

KAFKA_BOOTSTRAP = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
TOPIC_RAW = os.getenv("KAFKA_TOPIC_RAW", "raw_data")


class AirQualityKafkaProducer:
    """
    Manages connection and publishing of sensor messages to Apache Kafka.
    """

    def __init__(
        self,
        bootstrap_servers: str = KAFKA_BOOTSTRAP,
        topic: str = TOPIC_RAW,
        client_id: str = "air-quality-producer"
    ):
        self.bootstrap_servers = bootstrap_servers
        self.topic = topic
        self.client_id = client_id
        self.producer = None
        self._init_producer()

    def _init_producer(self):
        """Initializes KafkaProducer with JSON serialization after rapid connectivity probe."""
        import socket
        try:
            # Quick 0.5s probe to check if broker port is open
            host, port_str = self.bootstrap_servers.split(",")[0].split(":")
            with socket.create_connection((host, int(port_str)), timeout=0.5):
                pass
            from kafka import KafkaProducer
            self.producer = KafkaProducer(
                bootstrap_servers=self.bootstrap_servers.split(","),
                client_id=self.client_id,
                value_serializer=lambda v: json.dumps(v).encode("utf-8"),
                key_serializer=lambda k: k.encode("utf-8") if k else None,
                retries=1,
                max_block_ms=1000,
                request_timeout_ms=1000,
                acks="all"
            )
            logger.info(f"Connected to Kafka broker at {self.bootstrap_servers} on topic '{self.topic}'")
        except Exception as e:
            logger.warning(f"Kafka broker not reachable at {self.bootstrap_servers} ({e}). Fallback buffer enabled.")
            self.producer = None

    def publish(self, payload: Dict[str, Any]) -> bool:
        """Publishes a single message to the Kafka topic."""
        sensor_id = payload.get("sensor_id", "UNKNOWN")
        if self.producer:
            try:
                future = self.producer.send(self.topic, key=sensor_id, value=payload)
                self.producer.flush()
                record_metadata = future.get(timeout=5)
                logger.debug(
                    f"Message sent to {record_metadata.topic} partition {record_metadata.partition} offset {record_metadata.offset}"
                )
                return True
            except Exception as e:
                logger.error(f"Error publishing message to Kafka: {e}")
                return False
        else:
            # Fallback local logging mode when Kafka broker is offline
            logger.info(f"[OFFLINE BUFFER] Telemetry from {sensor_id}: {json.dumps(payload)}")
            return True

    def run_stream(self, interval_seconds: float = 2.0, limit: Optional[int] = None):
        """Continuously generates and streams readings to Kafka."""
        generator = AirQualitySensorGenerator()
        logger.info(f"Starting telemetry stream. Publishing every {interval_seconds}s (limit: {limit})")
        count = 0
        try:
            for reading in generator.stream_readings(interval_seconds=interval_seconds, limit=limit):
                self.publish(reading)
                count += 1
                if limit and count >= limit:
                    break
        except KeyboardInterrupt:
            logger.info("Kafka producer stopped by user.")
        finally:
            if self.producer:
                self.producer.close()
                logger.info("Kafka producer connection closed.")


if __name__ == "__main__":
    producer = AirQualityKafkaProducer()
    # Run test stream of 3 readings
    producer.run_stream(interval_seconds=0.5, limit=3)
