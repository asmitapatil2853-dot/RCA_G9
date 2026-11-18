import os
import pandas as pd
import networkx as nx

ANOMALY_FILE = "data/processed_logs/anomaly_results.csv"
RCA_OUTPUT_FILE = "data/processed_logs/rca_reports.csv"

def build_service_dependency_graph():
    G = nx.DiGraph()
    dependencies = [
        ("API-Gateway", "Auth-Service"),
        ("API-Gateway", "Order-Service"),
        ("Order-Service", "Database-Service"),
        ("Auth-Service", "K8s-Infra-Node"),
        ("Database-Service", "K8s-Infra-Node")
    ]
    G.add_edges_from(dependencies)
    return G

def run_root_cause_analysis():
    if not os.path.exists(ANOMALY_FILE):
        print(f"[ERROR] '{ANOMALY_FILE}' not found! Run 3_anomaly_detector.py first.")
        return

    df = pd.read_csv(ANOMALY_FILE)
    anomalies = df[df["status"] == "Anomaly"].copy()

    G = build_service_dependency_graph()
    rca_reports = []

    for req_id, group in anomalies.groupby("request_id"):
        group = group.sort_values("timestamp")
        affected_services = group["service"].unique().tolist()

        root_candidates = []
        for svc in affected_services:
            downstream_services = list(G.successors(svc))
            if not any(dep in affected_services for dep in downstream_services):
                root_candidates.append(svc)

        if root_candidates:
            candidate_logs = group[group["service"].isin(root_candidates)]
            root_cause_svc = candidate_logs.iloc[0]["service"]
            evidence_log = candidate_logs.iloc[0]["message"]
            incident_time = candidate_logs.iloc[0]["timestamp"]
        else:
            root_cause_svc = group.iloc[0]["service"]
            evidence_log = group.iloc[0]["message"]
            incident_time = group.iloc[0]["timestamp"]

        cascading_services = [s for s in affected_services if s != root_cause_svc]
        cascading_str = ", ".join(cascading_services) if cascading_services else "None (Isolated Failure)"

        recommendations = {
            "Database-Service": "Scale PostgreSQL connection pool, optimize slow queries, and verify primary DB health.",
            "K8s-Infra-Node": "Increase Kubernetes pod memory limits, check node resource allocation, and reschedule crashed pods.",
            "Auth-Service": "Verify Redis session store connectivity and restart Auth-Service replicas.",
            "Order-Service": "Inspect order worker queue and configure circuit-breaker timeouts.",
            "API-Gateway": "Check upstream routing rules, load balancer health, and rate-limiting thresholds."
        }

        rca_reports.append({
            "request_id": req_id,
            "incident_time": incident_time,
            "probable_root_cause": root_cause_svc,
            "cascading_failures": cascading_str,
            "total_affected_services": len(affected_services),
            "evidence_log": evidence_log,
            "recommended_action": recommendations.get(root_cause_svc, "Inspect service telemetry immediately.")
        })

    rca_df = pd.DataFrame(rca_reports)
    rca_df.to_csv(RCA_OUTPUT_FILE, index=False)

    print("==================================================")
    print("[SUCCESS] Multi-Layer Root-Cause Analysis Completed!")
    print(f"Total Correlated Incidents : {len(rca_df)}")
    print("\n--- Identified Root Causes Summary ---")
    print(rca_df["probable_root_cause"].value_counts().to_string())
    print("==================================================")

if __name__ == "__main__":
    run_root_cause_analysis()