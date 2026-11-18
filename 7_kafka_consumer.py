import os
import json
from kafka import KafkaConsumer
from kafka.errors import NoBrokersAvailable

KAFKA_BROKER = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
KAFKA_TOPIC = "distributed-logs"
FALLBACK_STREAM_FILE = "data/raw_logs/kafka_topic_buffer.jsonl"
OUTPUT_LOG_FILE = "data/raw_logs/distributed_system_logs.log"

def consume_from_kafka():
    os.makedirs(os.path.dirname(OUTPUT_LOG_FILE), exist_ok=True)
    records = []

    print("==================================================")
    print(f"[KAFKA CONSUMER] Subscribing to Kafka Topic: '{KAFKA_TOPIC}'")

    try:
        consumer = KafkaConsumer(
            KAFKA_TOPIC,
            bootstrap_servers=[KAFKA_BROKER],
            auto_offset_reset="earliest",
            enable_auto_commit=True,
            group_id="logrca-drain3-consumer-group",
            value_deserializer=lambda m: json.loads(m.decode("utf-8")),
            consumer_timeout_ms=3000
        )
        for msg in consumer:
            records.append(msg.value)
        consumer.close()
        print(f"[SUCCESS] Consumed {len(records)} real-time events from Kafka Broker ({KAFKA_BROKER})!")
    except NoBrokersAvailable:
        if os.path.exists(FALLBACK_STREAM_FILE):
            with open(FALLBACK_STREAM_FILE, "r", encoding="utf-8") as f:
                for line in f:
                    if line.strip():
                        records.append(json.loads(line))
        print(f"[INFO] Consumed {len(records)} buffered Kafka topic events from '{FALLBACK_STREAM_FILE}'.")

    if records:
        with open(OUTPUT_LOG_FILE, "w", encoding="utf-8") as out:
            for ev in records:
                line = f"{ev['timestamp']} | {ev['level']} | {ev['service']} | {ev['request_id']} | {ev['message']}\n"
                out.write(line)
        print(f"[SUCCESS] Persisted ingested stream to '{OUTPUT_LOG_FILE}' for Drain3 parsing.")
    print("==================================================")

if __name__ == "__main__":
    consume_from_kafka()