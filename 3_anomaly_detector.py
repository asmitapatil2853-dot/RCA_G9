import os
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import IsolationForest

PARSED_LOG_FILE = "data/processed_logs/parsed_logs.csv"
OUTPUT_FILE = "data/processed_logs/anomaly_results.csv"

def detect_anomalies():
    if not os.path.exists(PARSED_LOG_FILE):
        print(f"[ERROR] '{PARSED_LOG_FILE}' not found! Run 2_log_parser.py first.")
        return

    df = pd.read_csv(PARSED_LOG_FILE)

    level_mapping = {"INFO": 0, "WARNING": 1, "ERROR": 10, "FATAL": 15}
    df["severity_score"] = df["level"].map(level_mapping).fillna(0)

    df["has_error_keyword"] = df["message"].str.contains(
        "timeout|failed|aborted|unreachable", case=False, regex=True
    ).astype(int) * 10

    vectorizer = TfidfVectorizer(ngram_range=(1, 2), max_features=25)
    tfidf_features = vectorizer.fit_transform(df["event_template"]).toarray()

    numerical_features = df[["severity_score", "has_error_keyword"]].values
    X_raw = np.hstack((tfidf_features, numerical_features))

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X_raw)

    iso_forest = IsolationForest(n_estimators=200, contamination=0.10, random_state=42)
    df["anomaly_pred"] = iso_forest.fit_predict(X_scaled)
    df["anomaly_score"] = np.round(iso_forest.decision_function(X_scaled), 4)

    df["status"] = np.where((df["anomaly_pred"] == -1) & (df["level"] == "ERROR"), "Anomaly", "Normal")

    df.to_csv(OUTPUT_FILE, index=False)

    anomalies = df[df["status"] == "Anomaly"]
    print("==================================================")
    print("[SUCCESS] ML Anomaly Detection Completed!")
    print(f"Total Logs Analyzed  : {len(df)}")
    print(f"Normal Events        : {len(df) - len(anomalies)}")
    print(f"Anomalies Detected   : {len(anomalies)}")
    print(f"Saved Location       : {OUTPUT_FILE}")
    print("\n--- Detected Anomalies by Service ---")
    print(anomalies["service"].value_counts().to_string())
    print("==================================================")

if __name__ == "__main__":
    detect_anomalies()