import os
import random
from datetime import datetime, timedelta

LOG_FOLDER = "data/raw_logs"
os.makedirs(LOG_FOLDER, exist_ok=True)

SERVICES = [
    "API-Gateway",
    "Auth-Service",
    "Order-Service",
    "Database-Service",
    "K8s-Infra-Node"
]

LOG_TEMPLATES = {
    "API-Gateway": {
        "INFO": ["HTTP 200 GET /api/v1/status routed in 18ms", "HTTP 201 POST /api/v1/orders routed in 42ms"],
        "WARNING": ["Upstream response latency high (890ms) on route /api/v1/orders", "Rate limiter threshold 80% reached"]
    },
    "Auth-Service": {
        "INFO": ["JWT token verified for user_id={uid}", "OAuth2 session refreshed for user_id={uid}"],
        "WARNING": ["Token verification latency spike (310ms) for user_id={uid}", "Redis cache miss for user_id={uid}"]
    },
    "Order-Service": {
        "INFO": ["Order processed order_id={oid} for user_id={uid}", "Inventory lock acquired for order_id={oid}"],
        "WARNING": ["Worker queue depth increasing (450 pending) for order_id={oid}", "Retry triggered for order_id={oid}"]
    },
    "Database-Service": {
        "INFO": ["Query SELECT orders executed in 11ms", "PostgreSQL connection pool healthy: 24/100 active"],
        "WARNING": ["Slow query detected (1420ms) on table orders_ledger", "Replication lag warning: 350ms"]
    },
    "K8s-Infra-Node": {
        "INFO": ["Pod healthcheck passed on worker-node-0{nid}", "Container memory usage nominal at 54%"],
        "WARNING": ["High CPU utilization (88%) on worker-node-0{nid}", "Disk I/O wait time elevated on node-0{nid}"]
    }
}

def generate_logs(total_requests=300):
    logs = []
    start_time = datetime.now() - timedelta(minutes=30)
    counts = {"INFO": 0, "WARNING": 0, "ERROR": 0}

    for i in range(total_requests):
        current_time = start_time + timedelta(seconds=i * 3)
        req_id = f"REQ-{1000 + i}"
        uid = random.randint(100, 999)
        oid = random.randint(5000, 9999)
        nid = random.randint(1, 4)

        # Scenario 1: Database Failure cascading to Order-Service & API-Gateway
        if 60 <= i <= 72 or 210 <= i <= 220:
            events = [
                (current_time, "Database-Service", "ERROR", f"FATAL: PostgreSQL connection pool exhausted (100/100) on db-primary"),
                (current_time + timedelta(milliseconds=45), "Order-Service", "ERROR", f"Transaction aborted: Database write timeout for order_id={oid}"),
                (current_time + timedelta(milliseconds=110), "API-Gateway", "ERROR", f"HTTP 504 Gateway Timeout returned for request {req_id}")
            ]
            for ts, svc, lvl, msg in events:
                logs.append(f"{ts.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]} | {svc} | {lvl} | {req_id} | {msg}")
                counts[lvl] += 1

        # Scenario 2: Infrastructure (K8s Node) Crash cascading to Auth-Service & API-Gateway
        elif 130 <= i <= 140:
            events = [
                (current_time, "K8s-Infra-Node", "ERROR", f"OOMKilled: Container auth-pod crashed due to memory limit on worker-node-0{nid}"),
                (current_time + timedelta(milliseconds=50), "Auth-Service", "ERROR", f"Authentication service unreachable: Connection refused for user_id={uid}"),
                (current_time + timedelta(milliseconds=95), "API-Gateway", "ERROR", f"HTTP 502 Bad Gateway: Upstream Auth-Service unavailable")
            ]
            for ts, svc, lvl, msg in events:
                logs.append(f"{ts.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]} | {svc} | {lvl} | {req_id} | {msg}")
                counts[lvl] += 1

        # Normal Distributed Traffic across all 5 layers
        else:
            for idx, svc in enumerate(SERVICES):
                ts = current_time + timedelta(milliseconds=idx * 20)
                lvl = "WARNING" if random.random() < 0.10 else "INFO"
                msg = random.choice(LOG_TEMPLATES[svc][lvl]).format(uid=uid, oid=oid, nid=nid)
                logs.append(f"{ts.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]} | {svc} | {lvl} | {req_id} | {msg}")
                counts[lvl] += 1

    file_path = os.path.join(LOG_FOLDER, "distributed_system.log")
    with open(file_path, "w", encoding="utf-8") as f:
        f.write("\n".join(logs))

    print("==================================================")
    print("[SUCCESS] Multi-Layer Distributed Logs Generated!")
    print(f"Total Log Lines : {len(logs)}")
    print(f"INFO: {counts['INFO']} | WARNING: {counts['WARNING']} | ERROR: {counts['ERROR']}")
    print("==================================================")

if __name__ == "__main__":
    generate_logs()