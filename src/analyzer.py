# -*- coding: utf-8 -*-
"""
analyzer.py — FINAL BULLETPROOF & COMPATIBLE VERSION
→ sklearn >=1.0 safe
→ No score/length mismatch ever
→ Handles missing columns & empty data
→ Crash-proof AI for Dash callbacks
"""

import os
from datetime import datetime
import pandas as pd
from sklearn.ensemble import IsolationForest

# ================================================
# PATHS
# ================================================
ANOMALY_LOG = "data/anomalies.log"
os.makedirs("data", exist_ok=True)

# ================================================
# 1. AI ANOMALY DETECTION (Isolation Forest)
# ================================================
def detect_anomalies(df: pd.DataFrame):
    """Detect anomalous processes using Isolation Forest"""

    if df is None or df.empty or len(df) < 8:
        return []

    required_features = [
        'cpu', 'memory_mb', 'threads',
        'disk_read_mb', 'disk_write_mb', 'ctx_switches'
    ]

    # Ensure all required columns exist
    for col in required_features:
        if col not in df.columns:
            df[col] = 0

    X = df[required_features].fillna(0).values

    try:
        model = IsolationForest(
            n_estimators=100,
            contamination=0.05,
            random_state=42,
            max_samples="auto"
        )

        preds = model.fit_predict(X)  # -1 = anomaly
        if not (preds == -1).any():
            return []

        scores = model.decision_function(X)

        anomaly_idx = df.index[preds == -1]
        anomalies = df.loc[anomaly_idx].copy()

        anomalies["score"] = [
            round(scores[df.index.get_loc(i)], 4) for i in anomalies.index
        ]
        anomalies["detected_at"] = datetime.now().strftime("%H:%M:%S")

        _log_anomalies(anomalies)

        return anomalies.to_dict("records")[:10]

    except Exception:
        return []

# ================================================
# 2. MEMORY LEAK DETECTION (Heuristic)
# ================================================
def detect_memory_leak(df: pd.DataFrame):
    if df is None or df.empty:
        return []

    leaks = []

    for _, proc in df.iterrows():
        try:
            name = proc.get("name", "Unknown")
            mem_mb = float(proc.get("memory_mb", 0))
            age_min = float(proc.get("age_min", 0))

            if age_min < 3 and mem_mb > 1500:
                leaks.append({
                    "name": name,
                    "pid": proc.get("pid"),
                    "memory_mb": mem_mb,
                    "age_min": age_min,
                    "warning": f"CRITICAL LEAK: {mem_mb:.0f} MB in {age_min:.1f} min!"
                })
            elif age_min < 10 and mem_mb > 800:
                leaks.append({
                    "name": name,
                    "pid": proc.get("pid"),
                    "memory_mb": mem_mb,
                    "age_min": age_min,
                    "warning": f"Possible leak: {mem_mb:.0f} MB in {age_min:.1f} min"
                })
        except Exception:
            continue

    return leaks

# ================================================
# 3. LOG ANOMALIES (SAFE)
# ================================================
def _log_anomalies(anomalies_df: pd.DataFrame):
    if anomalies_df is None or anomalies_df.empty:
        return

    try:
        with open(ANOMALY_LOG, "a", encoding="utf-8") as f:
            for _, row in anomalies_df.iterrows():
                time = row.get("detected_at", "--:--:--")
                name = row.get("name", "Unknown")
                pid = row.get("pid", "?")
                cpu = row.get("cpu", 0)
                ram = row.get("memory_mb", 0)
                score = row.get("score", 0)

                f.write(
                    f"{time} | {name} (PID {pid}) | "
                    f"CPU:{cpu}% RAM:{ram:.0f}MB Score:{score}\n"
                )
    except Exception:
        pass

# ================================================
# 4. LOAD RECENT ANOMALIES FOR DASH TIMELINE
# ================================================
def get_recent_anomalies():
    if not os.path.exists(ANOMALY_LOG):
        return []

    try:
        with open(ANOMALY_LOG, "r", encoding="utf-8") as f:
            lines = f.readlines()[-20:]

        data = []
        for line in lines:
            parts = line.strip().split("|", 2)
            if len(parts) == 3:
                data.append({
                    "time": parts[0].strip(),
                    "info": f"{parts[1].strip()} | {parts[2].strip()}"
                })
        return data

    except Exception:
        return []
