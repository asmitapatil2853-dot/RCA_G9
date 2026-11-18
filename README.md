# Intelligent Distributed Log Analysis & Root-Cause Detection (AIOps LogRCA)

**B.Tech CSE Final Year Project (Group G9)**  
An end-to-end AI-powered Observability and Root-Cause Analysis (RCA) platform designed to ingest multi-layer distributed system logs, parse unstructured events using Drain3, detect anomalies via Isolation Forest, isolate cascading failures using Causal Dependency Graphs, and visualize insights in an interactive dark-mode dashboard.

## System Architecture (5-Layer Distributed Topology)
1. **Log Ingestion & Simulation (`1_log_generator.py`)**: Simulates real-time distributed logs across `API-Gateway`, `Auth-Service`, `Order-Service`, `Database-Service`, and `K8s-Infra-Node`.
2. **Log Parsing & Normalization (`2_log_parser.py`)**: Extracts structured event templates (`<*>`) from raw logs using **Drain3**.
3. **Feature Engineering & ML Anomaly Detection (`3_anomaly_detector.py`)**: Combines TF-IDF n-grams with severity/keyword features and trains an **Isolation Forest** model.
4. **Graph-Based Root-Cause Analysis (`4_rca_engine.py`)**: Uses **NetworkX** causal dependency traversal to separate true root causes from cascading downstream failures.
5. **Enterprise AIOps Dashboard (`5_dashboard.py`)**: Built with **Streamlit** and **Plotly** featuring SLA Gauges, Smartscape Causal Topology, Span Waterfall Flamegraphs, and JSON Trace Inspectors.
6. **Data Warehouse & Graph Export (`6_database_sync.py`)**: Persists structured tables into SQLite/PostgreSQL (`log_rca_warehouse.db`) and exports **Neo4j Cypher** topology scripts (`neo4j_graph.cypher`).

## Quick Start (Local Execution)
```bash
pip install -r requirements.txt
python 1_log_generator.py
python 2_log_parser.py
python 3_anomaly_detector.py
python 4_rca_engine.py
python 6_database_sync.py
streamlit run 5_dashboard.py