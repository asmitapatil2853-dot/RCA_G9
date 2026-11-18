import os
import pandas as pd
from drain3 import TemplateMiner
from drain3.template_miner_config import TemplateMinerConfig

RAW_LOG_FILE = "data/raw_logs/distributed_system.log"
PROCESSED_DIR = "data/processed_logs"
os.makedirs(PROCESSED_DIR, exist_ok=True)

def parse_logs():
    if not os.path.exists(RAW_LOG_FILE):
        print(f"[ERROR] '{RAW_LOG_FILE}' not found! Run 1_log_generator.py first.")
        return

    parsed_records = []
    with open(RAW_LOG_FILE, "r", encoding="utf-8") as f:
        for line in f:
            parts = [p.strip() for p in line.strip().split("|")]
            if len(parts) == 5:
                parsed_records.append({
                    "timestamp": parts[0],
                    "service": parts[1],
                    "level": parts[2],
                    "request_id": parts[3],
                    "message": parts[4]
                })

    df = pd.DataFrame(parsed_records)

    config = TemplateMinerConfig()
    config.profiling_enabled = False
    template_miner = TemplateMiner(config=config)

    event_templates = []
    cluster_ids = []

    for msg in df["message"]:
        result = template_miner.add_log_message(msg)
        event_templates.append(result["template_mined"])
        cluster_ids.append(result["cluster_id"])

    df["event_template"] = event_templates
    df["cluster_id"] = cluster_ids

    output_file = os.path.join(PROCESSED_DIR, "parsed_logs.csv")
    df.to_csv(output_file, index=False)

    print("==================================================")
    print("[SUCCESS] Log Parsing & Normalization Completed!")
    print(f"Total Parsed Records : {len(df)}")
    print(f"Unique Templates     : {df['event_template'].nunique()}")
    print(f"Saved Location       : {output_file}")
    print("\n--- Sample Drain3 Event Templates ---")
    for idx, tmpl in enumerate(df["event_template"].unique()[:8], 1):
        print(f" {idx}. {tmpl}")
    print("==================================================")

if __name__ == "__main__":
    parse_logs()