import os
import json
import time
import random
from datetime import datetime, timedelta
from kafka import KafkaProducer
from kafka.errors import NoBrokersAvailable

KAFKA_BROKER = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
KAFKA_TOPIC = "distributed-logs"
FALLBACK_STREAM_FILE = "data/raw_logs/kafka_topic_buffer.jsonl"

def generate_distributed_events(num_traces=250):
    """Generates multi-layer distributed system log events with cascading failures."""
    base_time = datetime(2026, 11, 18, 0, 0, 0)
    events = []

    for i in range(num_traces):
        req_id = f"REQ-{1000 + i}"
        ts = base_time + timedelta(seconds=i * 3)
        scenario = random.choices(["healthy", "db_pool_crash", "k8s_oom_crash"], weights=[0.84, 0.10, 0.06])[0]

        if scenario == "healthy":
            events.append({"timestamp": ts.strftime("%Y-%m-%d %H:%M:%S"), "level": "INFO", "service": "API-Gateway", "request_id": req_id, "message": f"Incoming POST /api/v1/orders routed successfully for {req_id}"})
            events.append({"timestamp": (ts + timedelta(milliseconds=15)).strftime("%Y-%m-%d %H:%M:%S"), "level": "INFO", "service": "Auth-Service", "request_id": req_id, "message": f"JWT token validated for user_session_{random.randint(100,999)}"})
            events.append({"timestamp": (ts + timedelta(milliseconds=35)).strftime("%Y-%m-%d %H:%M:%S"), "level": "INFO", "service": "Order-Service", "request_id": req_id, "message": f"Order payload verified for order_id={random.randint(5000,9999)}"})
            events.append({"timestamp": (ts + timedelta(milliseconds=55)).strftime("%Y-%m-%d %H:%M:%S"), "level": "INFO", "service": "Database-Service", "request_id": req_id, "message": f"COMMIT transaction completed in {random.randint(8,22)}ms"})
            events.append({"timestamp": (ts + timedelta(milliseconds=70)).strftime("%Y-%m-%d %H:%M:%S"), "level": "INFO", "service": "K8s-Infra-Node", "request_id": req_id, "message": f"Pod cpu_util={random.randint(25,55)}% mem_util={random.randint(40,65)}%"})

        elif scenario == "db_pool_crash":
            events.append({"timestamp": ts.strftime("%Y-%m-%d %H:%M:%S"), "level": "ERROR", "service": "Database-Service", "request_id": req_id, "message": "FATAL: PostgreSQL connection pool exhausted (100/100) on db-primary"})
            events.append({"timestamp": (ts + timedelta(milliseconds=40)).strftime("%Y-%m-%d %H:%M:%S"), "level": "ERROR", "service": "Order-Service", "request_id": req_id, "message": f"Transaction aborted: Database write timeout for order_id={random.randint(5000,9999)}"})
            events.append({"timestamp": (ts + timedelta(milliseconds=85)).strftime("%Y-%m-%d %H:%M:%S"), "level": "ERROR", "service": "API-Gateway", "request_id": req_id, "message": f"HTTP 504 Gateway Timeout returned for request {req_id}"})

        elif scenario == "k8s_oom_crash":
            events.append({"timestamp": ts.strftime("%Y-%m-%d %H:%M:%S"), "level": "ERROR", "service": "K8s-Infra-Node", "request_id": req_id, "message": "OOMKilled: Container auth-pod crashed due to memory limit on worker-node"})
            events.append({"timestamp": (ts + timedelta(milliseconds=30)).strftime("%Y-%m-%d %H:%M:%S"), "level": "ERROR", "service": "Auth-Service", "request_id": req_id, "message": f"Connection refused by upstream auth-pod worker for {req_id}"})
            events.append({"timestamp": (ts + timedelta(milliseconds=75)).strftime("%Y-%m-%d %H:%M:%S"), "level": "ERROR", "service": "API-Gateway", "request_id": req_id, "message": f"HTTP 502 Bad Gateway returned for request {req_id}"})

    return events

def stream_to_kafka():
    events = generate_distributed_events(num_traces=250)
    print("==================================================")
    print(f"[KAFKA PRODUCER] Initializing stream to topic: '{KAFKA_TOPIC}'")
    print(f"[KAFKA PRODUCER] Target Broker: {KAFKA_BROKER}")

    try:
        producer = KafkaProducer(
            bootstrap_servers=[KAFKA_BROKER],
            value_serializer=lambda v: json.dumps(v).encode("utf-8"),
            request_timeout_ms=3000
        )
        for ev in events:
            producer.send(KAFKA_TOPIC, value=ev)
        producer.flush()
        producer.close()
        print(f"[SUCCESS] Published {len(events)} JSON log messages to Kafka Topic '{KAFKA_TOPIC}'!")
    except NoBrokersAvailable:
        os.makedirs(os.path.dirname(FALLBACK_STREAM_FILE), exist_ok=True)
        with open(FALLBACK_STREAM_FILE, "w", encoding="utf-8") as f:
            for ev in events:
                f.write(json.dumps(ev) + "\n")
        print(f"[INFO] Live Kafka broker offline; buffered {len(events)} Kafka-formatted JSON events to '{FALLBACK_STREAM_FILE}'.")
    print("==================================================")

if __name__ == "__main__":
    stream_to_kafka()