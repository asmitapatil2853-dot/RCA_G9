import os
import json
import uuid
import pandas as pd
from fastapi import FastAPI, Query
from fastapi.responses import PlainTextResponse
from prometheus_client import CollectorRegistry, Gauge, Counter, generate_latest

app = FastAPI(
    title="Intelligent Distributed Log Analysis & RCA API",
    description="FastAPI Backend with Prometheus Metrics, OpenTelemetry Context & OpenSearch Indexer",
    version="1.0.0"
)

ANOMALY_FILE = "data/processed_logs/anomaly_results.csv"
RCA_FILE = "data/processed_logs/rca_reports.csv"
OPENSEARCH_INDEX_FILE = "data/processed_logs/opensearch_indexed_logs.json"

# --- Prometheus Metrics Registry ---
registry = CollectorRegistry()
TOTAL_LOGS_GAUGE = Gauge("logrca_ingested_logs_total", "Total distributed logs ingested via Kafka", registry=registry)
ANOMALY_GAUGE = Gauge("logrca_anomalies_detected_total", "Total ML anomalies detected by Isolation Forest", registry=registry)
INCIDENT_GAUGE = Gauge("logrca_correlated_incidents_total", "Total root-cause incidents isolated", registry=registry)
SERVICE_ERROR_GAUGE = Gauge("logrca_service_error_rate_percent", "Error rate percentage per microservice", ["service"], registry=registry)
API_REQUEST_COUNTER = Counter("logrca_api_requests_total", "Total FastAPI requests served", ["endpoint"], registry=registry)


def sync_telemetry_and_opensearch():
    """Updates Prometheus gauges and builds OpenSearch-compatible indexed JSON documents with OpenTelemetry trace IDs."""
    if not os.path.exists(ANOMALY_FILE) or not os.path.exists(RCA_FILE):
        return None, None

    logs_df = pd.read_csv(ANOMALY_FILE)
    rca_df = pd.read_csv(RCA_FILE)

    TOTAL_LOGS_GAUGE.set(len(logs_df))
    ANOMALY_GAUGE.set(len(logs_df[logs_df["status"] == "Anomaly"]))
    INCIDENT_GAUGE.set(len(rca_df))

    for svc, group in logs_df.groupby("service"):
        err_pct = round((len(group[group["status"] == "Anomaly"]) / len(group)) * 100, 2)
        SERVICE_ERROR_GAUGE.labels(service=svc).set(err_pct)

    # Generate OpenSearch + OpenTelemetry structured index
    indexed_docs = []
    for _, row in logs_df.head(200).iterrows():
        indexed_docs.append({
            "_index": "distributed-logs-2026.11",
            "_id": str(uuid.uuid4()),
            "_source": {
                "timestamp": str(row["timestamp"]),
                "otel.trace_id": f"otel-{row['request_id'].lower()}",
                "service.name": row["service"],
                "log.level": row["level"],
                "ml.status": row["status"],
                "ml.anomaly_score": float(row["anomaly_score"]),
                "drain3.template": row["event_template"],
                "message": row["message"]
            }
        })

    with open(OPENSEARCH_INDEX_FILE, "w", encoding="utf-8") as f:
        json.dump(indexed_docs, f, indent=2)

    return logs_df, rca_df


@app.on_event("startup")
def startup_event():
    sync_telemetry_and_opensearch()


@app.get("/")
def health_check():
    API_REQUEST_COUNTER.labels(endpoint="/").inc()
    return {
        "status": "healthy",
        "service": "Intelligent Distributed Log Analysis & Root-Cause Detection",
        "stack": ["Kafka", "FastAPI", "Prometheus", "OpenTelemetry", "OpenSearch", "Drain3", "IsolationForest", "NetworkX", "Grafana"]
    }


@app.get("/metrics", response_class=PlainTextResponse)
def prometheus_metrics():
    """Exposes real-time system and ML anomaly metrics in Prometheus scrape format."""
    sync_telemetry_and_opensearch()
    return generate_latest(registry).decode("utf-8")


@app.get("/api/v1/rca")
def get_rca_reports():
    API_REQUEST_COUNTER.labels(endpoint="/api/v1/rca").inc()
    _, rca_df = sync_telemetry_and_opensearch()
    if rca_df is None:
        return {"error": "Pipeline data not generated yet."}
    return {"total_incidents": len(rca_df), "incidents": rca_df.to_dict(orient="records")}


@app.get("/api/v1/opensearch/search")
def search_indexed_logs(q: str = Query("", description="Search keyword in indexed logs")):
    API_REQUEST_COUNTER.labels(endpoint="/api/v1/opensearch/search").inc()
    logs_df, _ = sync_telemetry_and_opensearch()
    if logs_df is None:
        return {"hits": []}
    if q:
        filtered = logs_df[logs_df["message"].str.contains(q, case=False, na=False)]
    else:
        filtered = logs_df.head(25)
    return {"index": "distributed-logs-2026.11", "total_hits": len(filtered), "hits": filtered.to_dict(orient="records")}