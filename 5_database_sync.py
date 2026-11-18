import os
import sqlite3
import pandas as pd

PROCESSED_DIR = "data/processed_logs"
PARSED_FILE = os.path.join(PROCESSED_DIR, "parsed_logs.csv")
ANOMALY_FILE = os.path.join(PROCESSED_DIR, "anomaly_results.csv")
RCA_FILE = os.path.join(PROCESSED_DIR, "rca_reports.csv")

SQL_DB_PATH = os.path.join(PROCESSED_DIR, "log_rca_warehouse.db")
NEO4J_CYPHER_PATH = os.path.join(PROCESSED_DIR, "neo4j_graph.cypher")

def sync_to_relational_db():
    """
    Persists parsed logs, ML anomaly results, and RCA reports into a structured
    Relational SQL Warehouse (PostgreSQL-compatible schema).
    """
    if not (os.path.exists(PARSED_FILE) and os.path.exists(ANOMALY_FILE) and os.path.exists(RCA_FILE)):
        print("[ERROR] Processed CSV files missing! Run scripts 1 to 4 first.")
        return False

    parsed_df = pd.read_csv(PARSED_FILE)
    anomaly_df = pd.read_csv(ANOMALY_FILE)
    rca_df = pd.read_csv(RCA_FILE)

    conn = sqlite3.connect(SQL_DB_PATH)
    parsed_df.to_sql("parsed_logs", conn, if_exists="replace", index=False)
    anomaly_df.to_sql("anomaly_results", conn, if_exists="replace", index=False)
    rca_df.to_sql("rca_reports", conn, if_exists="replace", index=False)

    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM rca_reports")
    rca_count = cursor.fetchone()[0]
    conn.close()

    print("==================================================")
    print("[SUCCESS] Relational SQL Storage Layer Synced!")
    print(f"Database File       : {SQL_DB_PATH}")
    print("Tables Created      : parsed_logs, anomaly_results, rca_reports")
    print(f"Verified RCA Rows   : {rca_count}")
    return True

def generate_neo4j_cypher():
    """
    Generates Neo4j Cypher queries representing the Distributed Service Topology,
    Causal Dependencies, and Isolated Root Causes for Graph DB ingestion.
    """
    rca_df = pd.read_csv(RCA_FILE)
    root_causes = set(rca_df["probable_root_cause"].unique())

    services = [
        ("API-Gateway", "Edge-Gateway"),
        ("Auth-Service", "Microservice"),
        ("Order-Service", "Microservice"),
        ("Database-Service", "Relational-DB"),
        ("K8s-Infra-Node", "Infrastructure")
    ]

    dependencies = [
        ("API-Gateway", "Auth-Service"),
        ("API-Gateway", "Order-Service"),
        ("Order-Service", "Database-Service"),
        ("Auth-Service", "K8s-Infra-Node"),
        ("Database-Service", "K8s-Infra-Node")
    ]

    cypher_lines = [
        "// Neo4j Graph Database Schema & RCA Topology Ingestion",
        "MATCH (n) DETACH DELETE n;"
    ]

    for svc_name, layer in services:
        status = "ROOT_CAUSE" if svc_name in root_causes else "AFFECTED_OR_HEALTHY"
        node_var = svc_name.replace("-", "_")
        cypher_lines.append(
            f"CREATE ({node_var}:Service {{name: '{svc_name}', layer: '{layer}', rca_status: '{status}'}});"
        )

    for src, dst in dependencies:
        src_var = src.replace("-", "_")
        dst_var = dst.replace("-", "_")
        cypher_lines.append(
            f"CREATE ({src_var})-[:DEPENDS_ON]->({dst_var});"
        )

    with open(NEO4J_CYPHER_PATH, "w", encoding="utf-8") as f:
        f.write("\n".join(cypher_lines))

    print("--------------------------------------------------")
    print("[SUCCESS] Neo4j Graph Topology Exported!")
    print(f"Cypher Script Path  : {NEO4J_CYPHER_PATH}")
    print("==================================================")

if __name__ == "__main__":
    if sync_to_relational_db():
        generate_neo4j_cypher()