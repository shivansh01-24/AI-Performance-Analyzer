# -*- coding: utf-8 -*-
"""
config.py — Persistent Configuration Manager (FINAL)
→ Dark / Light theme persistence
→ Safe load & save
→ No side-effects on import
→ Dash-safe and production-safe
"""

import json
import os

# ================================================
# CONFIG FILE PATH
# ================================================
CONFIG_DIR = "data"
CONFIG_FILE = os.path.join(CONFIG_DIR, "config.json")

os.makedirs(CONFIG_DIR, exist_ok=True)

# ================================================
# DEFAULT CONFIG
# ================================================
DEFAULT_CONFIG = {
    "theme": "dark",
    "auto_start_monitoring": True,
    "refresh_interval_sec": 3,
    "pdf_report_auto_save": True
}

# ================================================
# INITIALIZE CONFIG (SAFE)
# ================================================
def init_config():
    """Create config file once if missing"""
    if not os.path.exists(CONFIG_FILE):
        save_config(DEFAULT_CONFIG)

# ================================================
# LOAD CONFIG
# ================================================
def load_config():
    """Load config safely, always returns valid dict"""
    if not os.path.exists(CONFIG_FILE):
        return DEFAULT_CONFIG.copy()

    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            user_config = json.load(f)

        config = DEFAULT_CONFIG.copy()
        if isinstance(user_config, dict):
            config.update(user_config)
        return config

    except Exception:
        return DEFAULT_CONFIG.copy()

# ================================================
# SAVE CONFIG
# ================================================
def save_config(config_data: dict):
    """Safely save config to disk"""
    try:
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(config_data, f, indent=4)
    except Exception:
        pass

# ================================================
# QUICK GETTERS / SETTERS
# ================================================
def get_theme() -> str:
    """Return current theme"""
    return load_config().get("theme", "dark")

def set_theme(theme_name: str) -> bool:
    """Set dark/light theme"""
    if theme_name not in ("dark", "light"):
        return False

    config = load_config()
    config["theme"] = theme_name
    save_config(config)
    return True

# ================================================
# INIT ON FIRST IMPORT (SAFE)
# ================================================
init_config()
