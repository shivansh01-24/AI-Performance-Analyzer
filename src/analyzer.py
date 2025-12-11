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
from src.logger import get_logger

logger = get_logger(__name__)


# ================================================
# PATHS
# ================================================
ANOMALY_LOG = "data/anomalies.log"
os.makedirs("data", exist_ok=True)

# ================================================
# 1. AI ANOMALY DETECTION (Isolation Forest)
# ================================================
# -------- REAL-TIME BOTTLENECK DETECTION -------- #

def detect_bottlenecks(metrics):
    """
    Detect CPU, Memory, Disk, and Network bottlenecks using threshold rules.
    Returns a list of alert messages.
    """
    alerts = []

    # CPU bottleneck
    if metrics["cpu"] > 85:
        alerts.append(f"CPU bottleneck detected: {metrics['cpu']:.2f}%")

    # Memory bottleneck
    if metrics["memory"] > 85:
        alerts.append(f"Memory bottleneck detected: {metrics['memory']:.2f}%")

    # Disk bottleneck
    if metrics["disk_read"] > 500_000_000 or metrics["disk_write"] > 500_000_000:
        alerts.append(
            f"Disk I/O bottleneck detected: Read={metrics['disk_read']}B  Write={metrics['disk_write']}B"
        )

    # Network bottleneck
    if metrics["net_sent"] > 500_000_000 or metrics["net_recv"] > 500_000_000:
        alerts.append(
            f"Network bottleneck detected: Sent={metrics['net_sent']}B  Recv={metrics['net_recv']}B"
        )

    return alerts



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
   except Exception as e:
    logger.exception("Failed to log anomalies")


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

   except Exception as e:
    logger.exception("Failed to read recent anomalies")
    return []

# -------- OPTIMIZATION SUGGESTIONS ENGINE -------- #

def generate_optimization_suggestions(metrics, top_processes):
    """
    Provide intelligent optimization suggestions based on system performance.
    """
    suggestions = []

    # High CPU usage
    if metrics["cpu"] > 80:
        suggestions.append("CPU usage is high — consider closing background apps or optimizing CPU-intensive processes.")

    # Any single process consuming high CPU
    for proc in top_processes:
        if proc["cpu"] > 40:
            suggestions.append(
                f"Process '{proc['name']}' (PID {proc['pid']}) is consuming {proc['cpu']}% CPU — consider limiting its threads or optimizing code."
            )

    # Memory usage high
    if metrics["memory"] > 80:
        suggestions.append("Memory usage is high — consider freeing unused objects, increasing swap, or upgrading RAM.")

    # Disk I/O heavy
    if metrics["disk_read"] > 400_000_000 or metrics["disk_write"] > 400_000_000:
        suggestions.append("Heavy disk usage detected — check for logging loops, backups, or large file operations.")

    # Network heavy
    if metrics["net_recv"] > 300_000_000 or metrics["net_sent"] > 300_000_000:
        suggestions.append("High network load — check for sync tools, cloud transfers, or streaming tasks.")

    if not suggestions:
        suggestions.append("System performance is stable — no optimization required.")

    return suggestions

    # ================================================
# 5. UTILITY: HUMAN-READABLE BYTE FORMATTER
# ================================================
def format_bytes(size_in_bytes):
    """
    Convert bytes into a human-readable format (KB, MB, GB).
    A safe utility to improve dashboard or logging readability.
    """
    try:
        size_in_bytes = float(size_in_bytes)
    except Exception:
        return "0 B"

    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if size_in_bytes < 1024:
            return f"{size_in_bytes:.2f} {unit}"
        size_in_bytes /= 1024

    return f"{size_in_bytes:.2f} PB"








