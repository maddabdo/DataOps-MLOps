"""
Unit Tests: Kafka Producer & Consumer Simulation Wrappers
Air Quality Monitoring – Real-Time Anomaly Detection Platform
"""

import pytest
from ingestion.kafka_producer import AirQualityKafkaProducer
from ingestion.kafka_consumer import AirQualityKafkaConsumer


def test_producer_initialization():
    producer = AirQualityKafkaProducer(bootstrap_servers="localhost:9092")
    assert producer.topic == "raw_data"


def test_producer_publish_fallback():
    producer = AirQualityKafkaProducer(bootstrap_servers="localhost:9092")
    test_reading = {
        "sensor_id": "CAP_001",
        "timestamp": "2026-11-15T10:00:00Z",
        "measurements": {"pm2_5": 10.0, "pm10": 20.0, "no2": 30.0, "o3": 40.0, "temperature": 20.0, "humidity": 50.0},
        "status": "active"
    }
    # Should cleanly publish or buffer without raising unhandled exception
    res = producer.publish(test_reading)
    assert res is True


def test_consumer_initialization():
    consumer = AirQualityKafkaConsumer(bootstrap_servers="localhost:9092")
    assert "raw_data" in consumer.topics
    consumer.close()
