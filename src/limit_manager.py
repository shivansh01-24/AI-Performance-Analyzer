# -*- coding: utf-8 -*-
"""
limit_manager.py — FINAL BULLETPROOF VERSION
→ Exact whitelist matching (NO substring bug)
→ Pattern-based rule matching (contains)
→ Safe auto kill / suspend
→ Empty-process safe
"""

import json
import os
from src.monitor import get_processes_full, safe_action

# ================================================
# PATHS & FOLDERS
# ================================================
DATA_DIR = "data"
os.makedirs(DATA_DIR, exist_ok=True)

LIMITS_FILE = os.path.join(DATA_DIR, "user_limits.json")
WHITELIST_FILE = os.path.join(DATA_DIR, "whitelist.json")

# ================================================
# SAFE JSON LOAD / SAVE
# ================================================
def load_json(file_path, default=None):
    if default is None:
        default = {}
    if not os.path.exists(file_path):
        return default
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return default

def save_json(file_path, data):
    try:
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
    except Exception:
        pass

# ================================================
# MAIN LIMIT ENFORCEMENT
# ================================================
def enforce_limits():
    limits = load_json(LIMITS_FILE, {})
    whitelist = load_json(WHITELIST_FILE, {"apps": []})

    # Exact-match whitelist only
    whitelist_exact = {app.lower() for app in whitelist.get("apps", [])}

    alerts = []
    df = get_processes_full()

    # ✅ FIX: Proper empty check
    if df.empty or "name" not in df.columns:
        return []

    for app_pattern, rules in limits.items():
        # Match by CONTAINS
        matched = df[df["name"].str.contains(app_pattern, case=False, na=False)]

        for _, proc in matched.iterrows():
            pid = proc["pid"]
            name = proc["name"]
            full_name_lower = name.lower()

            # ✅ Exact whitelist match
            if full_name_lower in whitelist_exact:
                continue

            violations = []
            action = rules.get("action", "kill").lower()

            if rules.get("cpu") is not None and proc["cpu"] > rules["cpu"]:
                violations.append(f"CPU {proc['cpu']}% > {rules['cpu']}%")

            if rules.get("ram") is not None and proc["memory_mb"] > rules["ram"]:
                violations.append(f"RAM {proc['memory_mb']:.0f}MB > {rules['ram']}MB")

            if rules.get("time") is not None and proc["age_min"] > rules["time"]:
                violations.append(f"Age {proc['age_min']:.1f}min > {rules['time']}min")

            if violations:
                success, _ = safe_action(pid, action)
                status = "KILLED" if success else "FAILED"
                alerts.append(
                    f"{status}: {name} ({pid}) → {', '.join(violations)}"
                )

    return alerts

# ================================================
# RULE MANAGEMENT
# ================================================
def add_limit(app_name: str, cpu=None, ram=None, time=None, action: str = "kill"):
    limits = load_json(LIMITS_FILE, {})
    limits[app_name.lower()] = {
        "cpu": cpu,
        "ram": ram,
        "time": time,
        "action": action.lower()
    }
    save_json(LIMITS_FILE, limits)

def remove_limit(app_name: str):
    limits = load_json(LIMITS_FILE, {})
    key = app_name.lower()
    if key in limits:
        del limits[key]
        save_json(LIMITS_FILE, limits)

def get_limits():
    return load_json(LIMITS_FILE, {})

# ================================================
# WHITELIST MANAGEMENT (EXACT MATCH)
# ================================================
def add_to_whitelist(app_name: str):
    wl = load_json(WHITELIST_FILE, {"apps": []})
    if app_name.lower() not in [a.lower() for a in wl["apps"]]:
        wl["apps"].append(app_name)
        save_json(WHITELIST_FILE, wl)

def remove_from_whitelist(app_name: str):
    wl = load_json(WHITELIST_FILE, {"apps": []})
    wl["apps"] = [a for a in wl["apps"] if a.lower() != app_name.lower()]
    save_json(WHITELIST_FILE, wl)

def get_whitelist():
    return load_json(WHITELIST_FILE, {"apps": []})
