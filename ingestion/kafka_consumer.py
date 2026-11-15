#!/usr/bin/env python3
"""
Apache Kafka Consumer for Air Quality Telemetry
Air Quality Monitoring – Real-Time Anomaly Detection Platform

Subscribes to topics:
- raw_data: unprocessed incoming sensor streams
- processed_data: cleaned and validated data
- anomalies: detected anomaly events and alarms
"""

import os
import sys
import json
import logging
from typing import Optional, Callable, Dict, Any
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("KafkaConsumer")

KAFKA_BOOTSTRAP = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
TOPIC_RAW = os.getenv("KAFKA_TOPIC_RAW", "raw_data")
TOPIC_PROCESSED = os.getenv("KAFKA_TOPIC_PROCESSED", "processed_data")
TOPIC_ANOMALIES = os.getenv("KAFKA_TOPIC_ANOMALIES", "anomalies")
CONSUMER_GROUP = os.getenv("KAFKA_CONSUMER_GROUP", "air-quality-consumer-group")


class AirQualityKafkaConsumer:
    """
    Subscribes to Kafka topics and handles message deserialization.
    """

    def __init__(
        self,
        topics: Optional[list] = None,
        bootstrap_servers: str = KAFKA_BOOTSTRAP,
        group_id: str = CONSUMER_GROUP,
        auto_offset_reset: str = "latest"
    ):
        self.topics = topics or [TOPIC_RAW]
        self.bootstrap_servers = bootstrap_servers
        self.group_id = group_id
        self.auto_offset_reset = auto_offset_reset
        self.consumer = None
        self._init_consumer()

    def _init_consumer(self):
        """Initializes KafkaConsumer instance after fast socket probe."""
        import socket
        try:
            host, port_str = self.bootstrap_servers.split(",")[0].split(":")
            with socket.create_connection((host, int(port_str)), timeout=0.5):
                pass
            from kafka import KafkaConsumer
            self.consumer = KafkaConsumer(
                *self.topics,
                bootstrap_servers=self.bootstrap_servers.split(","),
                group_id=self.group_id,
                auto_offset_reset=self.auto_offset_reset,
                enable_auto_commit=True,
                value_deserializer=lambda m: json.loads(m.decode("utf-8")),
                key_deserializer=lambda k: k.decode("utf-8") if k else None,
                consumer_timeout_ms=5000
            )
            logger.info(f"Subscribed to topics: {self.topics} via group '{self.group_id}'")
        except Exception as e:
            logger.warning(f"Kafka broker not reachable at {self.bootstrap_servers} ({e}). Consumer running in simulation mode.")
            self.consumer = None

    def listen(self, callback: Optional[Callable[[Dict[str, Any]], None]] = None, max_messages: Optional[int] = None):
        """
        Polls for messages and invokes callback on each message.
        """
        if not self.consumer:
            logger.info("[SIMULATION CONSUMER] No Kafka broker detected. Consumer waiting...")
            return

        count = 0
        logger.info("Listening for messages...")
        try:
            for message in self.consumer:
                payload = message.value
                logger.info(f"Received from topic '{message.topic}' | Partition: {message.partition} | Offset: {message.offset}")
                if callback:
                    callback(payload)
                count += 1
                if max_messages and count >= max_messages:
                    break
        except Exception as e:
            logger.error(f"Consumer loop error: {e}")
        finally:
            self.close()

    def close(self):
        if self.consumer:
            self.consumer.close()
            logger.info("Kafka consumer closed.")


if __name__ == "__main__":
    consumer = AirQualityKafkaConsumer()
    print("Kafka Consumer initialized successfully.")
