# -*- coding: utf-8 -*-
"""
AI-Powered OS Process Analyzer - Single File Complete Solution
Real-time system monitoring, anomaly detection, forecasting, and process control
"""

import os
import json
import sys
import psutil
import pandas as pd
import numpy as np
from datetime import datetime
from pathlib import Path
import logging
from logging.handlers import RotatingFileHandler

# Dash and Plotly
import dash
from dash import html, dcc, Input, Output, State, callback_context, dash_table
import plotly.graph_objects as go
import plotly.express as px

# ML Libraries
from sklearn.ensemble import IsolationForest
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
import joblib

# PDF Report
try:
    from reportlab.lib.pagesizes import A4
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.lib import colors
    from reportlab.lib.enums import TA_CENTER
    PDF_AVAILABLE = True
except:
    PDF_AVAILABLE = False

# ================================================
# SETUP & CONFIGURATION
# ================================================
DATA_DIR = "data"
REPORTS_DIR = "reports"
LOGS_DIR = "logs"

for dir_path in [DATA_DIR, REPORTS_DIR, LOGS_DIR]:
    os.makedirs(dir_path, exist_ok=True)

HISTORY_CSV = os.path.join(DATA_DIR, "history.csv")
ANOMALY_LOG = os.path.join(DATA_DIR, "anomalies.log")
LIMITS_FILE = os.path.join(DATA_DIR, "user_limits.json")
WHITELIST_FILE = os.path.join(DATA_DIR, "whitelist.json")
CONFIG_FILE = os.path.join(DATA_DIR, "config.json")
FORECAST_MODEL = os.path.join(DATA_DIR, "cpu_forecast_model.pkl")
LOG_FILE = os.path.join(LOGS_DIR, "app.log")

# Logger Setup
logger = logging.getLogger("ai_analyzer")
logger.setLevel(logging.INFO)
if not logger.handlers:
    fh = RotatingFileHandler(LOG_FILE, maxBytes=1000000, backupCount=3)
    fh.setFormatter(logging.Formatter('[%(asctime)s] [%(levelname)s] %(message)s', datefmt='%Y-%m-%d %H:%M:%S'))
    logger.addHandler(fh)
    ch = logging.StreamHandler()
    ch.setFormatter(logging.Formatter('[%(levelname)s] %(message)s'))
    logger.addHandler(ch)

# ================================================
# CONFIGURATION MANAGEMENT
# ================================================
def load_config():
    default = {"theme": "dark", "refresh_interval": 3}
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r") as f:
                config = json.load(f)
                default.update(config)
        except:
            pass
    return default

def save_config(config):
    try:
        with open(CONFIG_FILE, "w") as f:
            json.dump(config, f, indent=2)
    except:
        pass

def get_theme():
    return load_config().get("theme", "dark")

# ================================================
# SYSTEM MONITORING
# ================================================
def get_system_stats():
    """Get comprehensive system statistics"""
    try:
        cpu = round(psutil.cpu_percent(interval=0.3), 1)
        cpu_cores = psutil.cpu_percent(percpu=True)
        vm = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        net = psutil.net_io_counters()
        
        return {
            'cpu': cpu,
            'cpu_cores': cpu_cores,
            'ram_percent': vm.percent,
            'ram_used_gb': round(vm.used / (1024**3), 2),
            'ram_total_gb': round(vm.total / (1024**3), 2),
            'ram_available_gb': round(vm.available / (1024**3), 2),
            'processes': len(psutil.pids()),
            'boot_time': datetime.fromtimestamp(psutil.boot_time()).strftime("%Y-%m-%d %H:%M"),
            'disk_percent': disk.percent,
            'disk_free_gb': round(disk.free / (1024**3), 2),
            'net_sent_mb': round(net.bytes_sent / (1024**2), 2),
            'net_recv_mb': round(net.bytes_recv / (1024**2), 2),
        }
    except Exception as e:
        logger.error(f"Error getting system stats: {e}")
        return {
            'cpu': 0.0, 'cpu_cores': [0] * 4, 'ram_percent': 0.0,
            'ram_used_gb': 0.0, 'ram_total_gb': 0.0, 'ram_available_gb': 0.0,
            'processes': 0, 'boot_time': "Unknown", 'disk_percent': 0.0,
            'disk_free_gb': 0.0, 'net_sent_mb': 0.0, 'net_recv_mb': 0.0
        }

def get_gpu():
    """Get GPU statistics"""
    try:
        import GPUtil
        gpus = GPUtil.getGPUs()
        if gpus:
            return [{'name': g.name, 'load': round(g.load * 100, 1), 
                    'memory_used': g.memoryUsed, 'memory_total': g.memoryTotal} for g in gpus]
    except:
        pass
    return None

def get_processes_full():
    """Get all processes with full metrics"""
    data = []
    for p in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_info', 'num_threads', 
                                   'create_time', 'status', 'ppid']):
        try:
            with p.oneshot():
                cpu = p.cpu_percent(interval=None)
                mem_info = p.memory_info()
                age_sec = (datetime.now() - datetime.fromtimestamp(p.create_time())).total_seconds()
                
                data.append({
                    'pid': p.pid,
                    'name': p.name(),
                    'cpu': round(cpu, 1),
                    'memory_mb': round(mem_info.rss / (1024**2), 1),
                    'threads': p.num_threads(),
                    'age_min': round(age_sec / 60, 1),
                    'status': p.status(),
                    'parent': p.ppid()
                })
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            continue
        except Exception:
            continue
    
    df = pd.DataFrame(data)
    if df.empty:
        return df
    return df.sort_values('memory_mb', ascending=False).reset_index(drop=True)

def log_history():
    """Log system metrics to history"""
    try:
        stats = get_system_stats()
        record = {
            'time': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'cpu': stats['cpu'],
            'memory': stats['ram_percent'],
            'processes': stats['processes']
        }
        df = pd.DataFrame([record])
        
        # Auto-trim to 500 lines
        if os.path.exists(HISTORY_CSV):
            with open(HISTORY_CSV, 'r') as f:
                lines = f.readlines()
            if len(lines) > 500:
                with open(HISTORY_CSV, 'w') as f:
                    f.writelines(lines[-500:])
        
        if not os.path.exists(HISTORY_CSV):
            df.to_csv(HISTORY_CSV, index=False)
        else:
            df.to_csv(HISTORY_CSV, mode='a', header=False, index=False)
    except Exception as e:
        logger.error(f"Error logging history: {e}")

# ================================================
# PROCESS CONTROL
# ================================================
def kill_process(pid):
    """Kill a process"""
    try:
        p = psutil.Process(pid)
        name = p.name()
        p.kill()
        return True, f"{name} (PID {pid}) killed"
    except psutil.NoSuchProcess:
        return False, f"Process {pid} not found"
    except psutil.AccessDenied:
        return False, f"Access denied (Run as Admin)"
    except Exception as e:
        return False, f"Error: {str(e)}"

def terminate_process(pid):
    """Terminate a process"""
    try:
        p = psutil.Process(pid)
        name = p.name()
        p.terminate()
        return True, f"{name} (PID {pid}) terminated"
    except psutil.NoSuchProcess:
        return False, f"Process {pid} not found"
    except psutil.AccessDenied:
        return False, f"Access denied"
    except Exception as e:
        return False, f"Error: {str(e)}"

# ================================================
# AI ANOMALY DETECTION
# ================================================
def detect_anomalies(df):
    """Detect anomalies using Isolation Forest"""
    if df is None or df.empty or len(df) < 3:
        return pd.DataFrame()
    
    try:
        numeric_cols = ['cpu', 'memory_mb', 'threads']
        available_cols = [col for col in numeric_cols if col in df.columns]
        if not available_cols:
            return pd.DataFrame()
        
        X = df[available_cols].fillna(0)
        if len(X) < 3:
            return pd.DataFrame()
        
        iso_forest = IsolationForest(contamination=0.1, random_state=42)
        anomaly_labels = iso_forest.fit_predict(X)
        anomaly_scores = iso_forest.score_samples(X)
        
        result = df.copy()
        result['anomaly'] = anomaly_labels == -1
        result['anomaly_score'] = -anomaly_scores
        result['detected_at'] = datetime.now().strftime("%H:%M:%S")
        
        anomalies = result[result['anomaly']]
        
        if not anomalies.empty:
            _log_anomalies(anomalies)
        
        return anomalies
    except Exception as e:
        logger.error(f"Anomaly detection failed: {e}")
        return pd.DataFrame()

def detect_memory_leak(df):
    """Detect potential memory leaks"""
    if df is None or df.empty:
        return []
    
    leaks = []
    for _, proc in df.iterrows():
        try:
            mem_mb = float(proc.get("memory_mb", 0))
            age_min = float(proc.get("age_min", 0))
            if age_min < 3 and mem_mb > 1500:
                leaks.append({
                    "name": proc.get("name", "Unknown"),
                    "pid": proc.get("pid"),
                    "memory_mb": mem_mb,
                    "warning": f"CRITICAL: {mem_mb:.0f} MB in {age_min:.1f} min!"
                })
        except:
            continue
    return leaks

def _log_anomalies(anomalies_df):
    """Log anomalies to file"""
    try:
        with open(ANOMALY_LOG, "a", encoding="utf-8") as f:
            for _, row in anomalies_df.iterrows():
                f.write(f"{row.get('detected_at', '--:--:--')} | {row.get('name', 'Unknown')} (PID {row.get('pid', '?')}) | "
                       f"CPU:{row.get('cpu', 0)}% RAM:{row.get('memory_mb', 0):.0f}MB\n")
    except:
        pass

def get_recent_anomalies(limit=20):
    """Get recent anomalies from log"""
    if not os.path.exists(ANOMALY_LOG):
        return []
    try:
        with open(ANOMALY_LOG, "r", encoding="utf-8") as f:
            lines = f.readlines()[-limit:]
        data = []
        for line in lines:
            parts = line.strip().split("|", 2)
            if len(parts) == 3:
                data.append({"time": parts[0].strip(), "info": f"{parts[1].strip()} | {parts[2].strip()}"})
        return data
    except:
        return []

# ================================================
# FORECASTING
# ================================================
def train_forecast_model():
    """Train CPU forecast model"""
    if not os.path.exists(HISTORY_CSV):
        return None, "No history data"
    
    try:
        df = pd.read_csv(HISTORY_CSV)
        if len(df) < 30:
            return None, f"Need 30 records, have {len(df)}"
        
        df["cpu_next"] = df["cpu"].shift(-1)
        df = df.dropna()
        if len(df) < 10:
            return None, "Not enough data"
        
        X = df[["cpu", "memory"]]
        y = df["cpu_next"]
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        model = LinearRegression()
        model.fit(X_train, y_train)
        score = model.score(X_test, y_test)
        
        joblib.dump(model, FORECAST_MODEL)
        return model, f"Model trained (R²={score:.3f})"
    except Exception as e:
        return None, f"Training failed: {str(e)}"

def load_forecast_model():
    """Load forecast model"""
    try:
        if os.path.exists(FORECAST_MODEL):
            return joblib.load(FORECAST_MODEL)
    except:
        pass
    return None

def predict_cpu_usage(current_cpu, current_mem):
    """Predict next CPU usage"""
    model = load_forecast_model()
    if model is None:
        return None
    try:
        prediction = model.predict([[current_cpu, current_mem]])
        return round(float(prediction[0]), 2)
    except:
        return None

def get_historical_data(limit=100):
    """Get historical metrics"""
    if not os.path.exists(HISTORY_CSV):
        return pd.DataFrame()
    try:
        df = pd.read_csv(HISTORY_CSV)
        return df.tail(limit)
    except:
        return pd.DataFrame()

# ================================================
# LIMIT MANAGEMENT
# ================================================
def load_json(file_path, default=None):
    if default is None:
        default = {}
    if not os.path.exists(file_path):
        return default
    try:
        with open(file_path, "r") as f:
            return json.load(f)
    except:
        return default

def save_json(file_path, data):
    try:
        with open(file_path, "w") as f:
            json.dump(data, f, indent=2)
    except:
        pass

def enforce_limits():
    """Enforce CPU/memory limits"""
    limits = load_json(LIMITS_FILE, {})
    whitelist = load_json(WHITELIST_FILE, {"apps": []})
    whitelist_exact = {app.lower() for app in whitelist.get("apps", [])}
    
    alerts = []
    df = get_processes_full()
    
    if df.empty:
        return []
    
    for app_pattern, rules in limits.items():
        matched = df[df["name"].str.contains(app_pattern, case=False, na=False)]
        for _, proc in matched.iterrows():
            name = proc["name"]
            if name.lower() in whitelist_exact:
                continue
            
            violations = []
            action = rules.get("action", "kill").lower()
            
            if rules.get("cpu") is not None and proc["cpu"] > rules["cpu"]:
                violations.append(f"CPU {proc['cpu']}% > {rules['cpu']}%")
            if rules.get("ram") is not None and proc["memory_mb"] > rules["ram"]:
                violations.append(f"RAM {proc['memory_mb']:.0f}MB > {rules['ram']}MB")
            
            if violations:
                pid = proc["pid"]
                success, _ = kill_process(pid) if action == "kill" else terminate_process(pid)
                status = "KILLED" if success else "FAILED"
                alerts.append(f"{status}: {name} (PID {pid}) → {', '.join(violations)}")
    
    return alerts

def add_limit(app_name, cpu=None, ram=None, action="kill"):
    """Add limit rule"""
    limits = load_json(LIMITS_FILE, {})
    limits[app_name.lower()] = {"cpu": cpu, "ram": ram, "action": action.lower()}
    save_json(LIMITS_FILE, limits)

def remove_limit(app_name):
    """Remove limit rule"""
    limits = load_json(LIMITS_FILE, {})
    if app_name.lower() in limits:
        del limits[app_name.lower()]
        save_json(LIMITS_FILE, limits)

def get_limits():
    """Get all limits"""
    return load_json(LIMITS_FILE, {})

def add_to_whitelist(app_name):
    """Add to whitelist"""
    wl = load_json(WHITELIST_FILE, {"apps": []})
    if app_name.lower() not in [a.lower() for a in wl["apps"]]:
        wl["apps"].append(app_name)
        save_json(WHITELIST_FILE, wl)

def remove_from_whitelist(app_name):
    """Remove from whitelist"""
    wl = load_json(WHITELIST_FILE, {"apps": []})
    wl["apps"] = [a for a in wl["apps"] if a.lower() != app_name.lower()]
    save_json(WHITELIST_FILE, wl)

def get_whitelist():
    """Get whitelist"""
    return load_json(WHITELIST_FILE, {"apps": []})

# ================================================
# PDF REPORT GENERATION
# ================================================
def generate_pdf_report():
    """Generate PDF report"""
    if not PDF_AVAILABLE:
        return "PDF generation not available (reportlab not installed)"
    
    try:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_path = os.path.join(REPORTS_DIR, f"Report_{timestamp}.pdf")
        
        doc = SimpleDocTemplate(report_path, pagesize=A4, topMargin=inch, bottomMargin=inch)
        story = []
        styles = getSampleStyleSheet()
        
        story.append(Paragraph("AI-POWERED OS PERFORMANCE REPORT", styles["Title"]))
        story.append(Spacer(1, 20))
        
        stats = get_system_stats()
        info_data = [
            ["Report Generated", datetime.now().strftime("%Y-%m-%d %H:%M:%S")],
            ["CPU Usage", f"{stats['cpu']:.1f}%"],
            ["RAM Usage", f"{stats['ram_percent']:.1f}%"],
            ["Total RAM", f"{stats['ram_total_gb']:.2f} GB"],
            ["Active Processes", str(stats['processes'])]
        ]
        
        info_table = Table(info_data, colWidths=[3*inch, 3*inch])
        info_table.setStyle(TableStyle([
            ('GRID', (0,0), (-1,-1), 1, colors.grey),
            ('BACKGROUND', (0,0), (-1,0), colors.lightgrey),
        ]))
        story.append(info_table)
        story.append(Spacer(1, 30))
        
        df = get_processes_full()
        if not df.empty:
            story.append(Paragraph("TOP 10 PROCESSES", styles["Heading2"]))
            table_data = [["Name", "PID", "CPU %", "RAM (MB)"]]
            for _, row in df.head(10).iterrows():
                table_data.append([
                    str(row.get('name', 'Unknown'))[:30],
                    str(row.get('pid', 'N/A')),
                    f"{row.get('cpu', 0):.1f}",
                    f"{row.get('memory_mb', 0):.0f}"
                ])
            proc_table = Table(table_data, repeatRows=1)
            proc_table.setStyle(TableStyle([
                ('GRID', (0,0), (-1,-1), 1, colors.grey),
                ('BACKGROUND', (0,0), (-1,0), colors.lightgrey),
            ]))
            story.append(proc_table)
        
        doc.build(story)
        return f"Report saved: {os.path.basename(report_path)}"
    except Exception as e:
        return f"PDF generation failed: {str(e)}"

# ================================================
# DASH APP - SINGLE PAGE WITH SECTIONS
# ================================================
app = dash.Dash(__name__, title="AI OS Analyzer", assets_folder="assets")
app.config.suppress_callback_exceptions = True

# CSS Styles inline
app.index_string = '''
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>{%title%}</title>
        {%favicon%}
        {%css%}
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #0f0f23; color: #e0e0ff; }
            .container { max-width: 1400px; margin: 0 auto; padding: 20px; }
            .header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 30px; padding: 20px; background: rgba(30, 30, 60, 0.8); border-radius: 10px; }
            .section { background: rgba(30, 30, 60, 0.8); padding: 25px; margin-bottom: 25px; border-radius: 10px; border: 1px solid rgba(0, 255, 150, 0.2); }
            .section h2 { color: #00ff96; margin-bottom: 20px; font-size: 24px; }
            .cards { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin-bottom: 30px; }
            .card { background: rgba(20, 20, 40, 0.9); padding: 20px; border-radius: 10px; text-align: center; border: 1px solid rgba(0, 255, 150, 0.3); }
            .card h4 { color: #a0a0cc; font-size: 12px; margin-bottom: 10px; }
            .card h2 { color: #00ff96; font-size: 36px; font-weight: bold; }
            button { background: rgba(0, 255, 150, 0.2); border: 1px solid #00ff96; color: #00ff96; padding: 10px 20px; border-radius: 8px; cursor: pointer; margin: 5px; }
            button:hover { background: rgba(0, 255, 150, 0.4); }
            input, select { padding: 8px; border-radius: 6px; border: 1px solid #00ff96; background: rgba(20, 20, 40, 0.9); color: #e0e0ff; margin: 5px; }
            .alert { padding: 10px; margin: 5px 0; border-radius: 6px; background: rgba(255, 51, 102, 0.2); border: 1px solid #ff3366; }
            .success { background: rgba(0, 255, 150, 0.2); border-color: #00ff96; }
        </style>
    </head>
    <body>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>
'''

app.layout = html.Div(className="container", children=[
    dcc.Interval(id="interval", interval=3000, n_intervals=0),
    dcc.Interval(id="limit-check", interval=5000, n_intervals=0),
    dcc.Store(id="theme-store", data=get_theme()),
    
    # Header
    html.Div(className="header", children=[
        html.Div([
            html.H1("🖥️ AI-Powered System Performance Monitor", style={"color": "#00ff96", "marginBottom": "5px"}),
            html.P("Real-time OS & Process Analysis with AI Anomaly Detection", style={"color": "#a0a0cc"}),
        ]),
        html.Div([
            html.Button("🌙 Toggle Theme", id="theme-btn"),
            html.Button("📄 PDF Report", id="pdf-btn"),
        ]),
    ]),
    
    # Status Messages
    html.Div(id="status-msg", style={"marginBottom": "20px"}),
    html.Div(id="alerts-container", style={"marginBottom": "20px"}),
    
    # Section 1: System Metrics
    html.Div(className="section", children=[
        html.H2("📊 System Metrics"),
        html.Div(id="stats-grid", className="cards"),
    ]),
    
    # Section 2: Graphs
    html.Div(className="section", children=[
        html.H2("📈 Performance Graphs"),
        html.Div([
            html.Div([dcc.Graph(id="cpu-heatmap", config={"displayModeBar": False})], style={"width": "48%", "display": "inline-block"}),
            html.Div([dcc.Graph(id="memory-timeline", config={"displayModeBar": False})], style={"width": "48%", "display": "inline-block", "marginLeft": "4%"}),
        ]),
        html.Div([
            html.Div([dcc.Graph(id="anomaly-timeline", config={"displayModeBar": False})], style={"width": "48%", "display": "inline-block"}),
            html.Div([dcc.Graph(id="cpu-forecast", config={"displayModeBar": False})], style={"width": "48%", "display": "inline-block", "marginLeft": "4%"}),
        ], style={"marginTop": "20px"}),
        html.Div([dcc.Graph(id="historical-trends", config={"displayModeBar": False})], style={"marginTop": "20px"}),
    ]),
    
    # Section 3: Process Management
    html.Div(className="section", children=[
        html.H2("⚙️ Process Management"),
        html.Div([
            dcc.Input(id="process-search", type="text", placeholder="Search processes...", style={"width": "300px"}),
            dcc.Input(id="kill-pid-input", type="number", placeholder="Enter PID", style={"width": "150px"}),
            html.Button("Kill", id="kill-pid-btn"),
            html.Button("Terminate", id="term-pid-btn"),
            html.Button("🔄 Refresh", id="refresh-processes"),
        ], style={"marginBottom": "20px"}),
        html.Div(id="process-table-container"),
        html.Div(id="process-action-result", style={"marginTop": "20px"}),
    ]),
    
    # Section 4: Limits & Rules
    html.Div(className="section", children=[
        html.H2("🛡️ Process Limits & Auto-Kill Rules"),
        html.Div([
            html.Div([
                html.H3("Add Limit Rule", style={"color": "#00ccff", "marginBottom": "15px"}),
                html.Label("Process Name:"), html.Br(),
                dcc.Input(id="limit-name", type="text", placeholder="e.g., chrome", style={"width": "100%", "marginBottom": "10px"}),
                html.Label("Max CPU %:"), html.Br(),
                dcc.Input(id="limit-cpu", type="number", placeholder="50", style={"width": "100%", "marginBottom": "10px"}),
                html.Label("Max RAM (MB):"), html.Br(),
                dcc.Input(id="limit-ram", type="number", placeholder="1000", style={"width": "100%", "marginBottom": "10px"}),
                html.Label("Action:"), html.Br(),
                dcc.Dropdown(id="limit-action", options=[{"label": "Kill", "value": "kill"}, {"label": "Terminate", "value": "terminate"}], 
                            value="kill", style={"width": "100%", "marginBottom": "10px"}),
                html.Button("➕ Add Limit", id="add-limit-btn", style={"width": "100%"}),
            ], style={"width": "48%", "display": "inline-block", "verticalAlign": "top"}),
            html.Div([
                html.H3("Whitelist (Protected)", style={"color": "#00ccff", "marginBottom": "15px"}),
                dcc.Input(id="whitelist-name", type="text", placeholder="e.g., explorer.exe", style={"width": "100%", "marginBottom": "10px"}),
                html.Button("➕ Add to Whitelist", id="add-whitelist-btn", style={"width": "100%", "marginBottom": "10px"}),
                html.Hr(style={"margin": "20px 0"}),
                html.Label("Remove from Whitelist:"), html.Br(),
                dcc.Input(id="remove-whitelist-name", type="text", placeholder="Enter process name", style={"width": "70%", "marginBottom": "10px"}),
                html.Button("❌ Remove", id="remove-whitelist-btn", style={"width": "28%", "marginLeft": "2%"}),
                html.Div(id="whitelist-list", style={"marginTop": "20px"}),
            ], style={"width": "48%", "display": "inline-block", "verticalAlign": "top", "marginLeft": "4%"}),
        ]),
        html.Div([
            html.Hr(style={"margin": "20px 0"}),
            html.Label("Remove Limit Rule:"), html.Br(),
            dcc.Input(id="remove-limit-name", type="text", placeholder="Enter process name pattern", style={"width": "70%", "marginBottom": "10px"}),
            html.Button("❌ Remove", id="remove-limit-btn", style={"width": "28%", "marginLeft": "2%"}),
        ], style={"marginTop": "20px"}),
        html.Div(id="limits-list", style={"marginTop": "20px"}),
    ]),
    
    # Section 5: Analytics & Insights
    html.Div(className="section", children=[
        html.H2("📊 Analytics & Insights"),
        html.Div([
            html.Div([dcc.Graph(id="process-distribution", config={"displayModeBar": False})], style={"width": "48%", "display": "inline-block"}),
            html.Div([dcc.Graph(id="resource-breakdown", config={"displayModeBar": False})], style={"width": "48%", "display": "inline-block", "marginLeft": "4%"}),
        ]),
        html.Div(id="analytics-stats", style={"marginTop": "20px"}),
    ]),
    
    # Section 6: Reports
    html.Div(className="section", children=[
        html.H2("📄 Reports & Logs"),
        html.Div([
            html.Button("📄 Generate PDF Report", id="generate-report-btn", style={"marginRight": "10px"}),
            html.Button("📊 View Anomaly Log", id="view-anomalies-btn"),
        ], style={"marginBottom": "20px"}),
        html.Div(id="reports-content"),
    ]),
])

# ================================================
# CALLBACKS
# ================================================
def plot_template():
    return "plotly_dark" if get_theme() == "dark" else "plotly_white"

@app.callback(
    [Output("stats-grid", "children"),
     Output("cpu-heatmap", "figure"),
     Output("memory-timeline", "figure"),
     Output("anomaly-timeline", "figure"),
     Output("cpu-forecast", "figure"),
     Output("historical-trends", "figure")],
    [Input("interval", "n_intervals")]
)
def update_dashboard(n):
    """Update all dashboard components"""
    try:
        log_history()
        stats = get_system_stats()
        df = get_processes_full()
        gpu = get_gpu()
        anomalies = detect_anomalies(df)
        
        gpu_load = gpu[0]["load"] if gpu else 0
        cpu_pred = predict_cpu_usage(stats['cpu'], stats['ram_percent'])
        
        # Metrics Cards
        cards = [
            html.Div(className="card", children=[
                html.H4("CPU USAGE"), html.H2(f"{stats['cpu']:.1f}%"),
                html.P(f"Forecast: {cpu_pred:.1f}%" if cpu_pred else "", style={"fontSize": "11px", "color": "#00ccff"})
            ]),
            html.Div(className="card", children=[
                html.H4("RAM USAGE"), html.H2(f"{stats['ram_percent']:.1f}%"),
                html.P(f"{stats['ram_available_gb']:.1f} GB free", style={"fontSize": "11px", "color": "#00ccff"})
            ]),
            html.Div(className="card", children=[
                html.H4("GPU USAGE"), html.H2(f"{gpu_load:.1f}%"),
            ]),
            html.Div(className="card", children=[
                html.H4("PROCESSES"), html.H2(f"{stats['processes']}"),
            ]),
            html.Div(className="card", children=[
                html.H4("ANOMALIES"), html.H2(f"{len(anomalies)}", style={"color": "#ff3366" if len(anomalies) > 0 else "#00ff96"}),
            ]),
            html.Div(className="card", children=[
                html.H4("DISK FREE"), html.H2(f"{stats['disk_free_gb']:.1f}GB"),
            ]),
        ]
        
        # CPU Heatmap
        cpu_fig = go.Figure(go.Heatmap(z=[stats["cpu_cores"]], colorscale="Viridis", showscale=True))
        cpu_fig.update_layout(template=plot_template(), height=300, margin=dict(l=0, r=0, t=0, b=0), title="CPU Core Usage")
        
        # Memory Timeline
        mem_df = df.sort_values("age_min").head(20) if not df.empty else pd.DataFrame()
        if not mem_df.empty:
            mem_fig = px.line(mem_df, x="age_min", y="memory_mb", color="name", 
                            labels={"age_min": "Age (min)", "memory_mb": "Memory (MB)"})
        else:
            mem_fig = go.Figure()
            mem_fig.add_annotation(text="No data", xref="paper", yref="paper", x=0.5, y=0.5)
        mem_fig.update_layout(template=plot_template(), height=300, title="Memory Usage Over Time")
        
        # Anomaly Timeline
        timeline = get_recent_anomalies()
        t_fig = go.Figure()
        if timeline:
            times = [x["time"] for x in timeline]
            t_fig.add_scatter(x=times, y=list(range(len(timeline))), mode="markers",
                            marker=dict(size=12, color="#ff3366"), text=[x["info"][:40] for x in timeline])
        else:
            t_fig.add_annotation(text="✓ No anomalies", xref="paper", yref="paper", x=0.5, y=0.5)
        t_fig.update_layout(template=plot_template(), height=300, title="Anomaly Timeline", showlegend=False)
        
        # CPU Forecast
        hist_df = get_historical_data(50)
        forecast_fig = go.Figure()
        if not hist_df.empty and len(hist_df) > 5:
            forecast_fig.add_trace(go.Scatter(x=hist_df['time'].tail(20), y=hist_df['cpu'], 
                                             mode='lines+markers', name='Actual CPU', line=dict(color='#00ff96')))
            if cpu_pred:
                forecast_fig.add_trace(go.Scatter(x=[hist_df['time'].iloc[-1], "Next"], 
                                                y=[hist_df['cpu'].iloc[-1], cpu_pred], mode='lines+markers',
                                                name='Forecast', line=dict(color='#ffaa00', dash='dash')))
        else:
            forecast_fig.add_annotation(text="Need more data", xref="paper", yref="paper", x=0.5, y=0.5)
        forecast_fig.update_layout(template=plot_template(), height=300, title="CPU Usage Forecast")
        
        # Historical Trends
        hist_fig = go.Figure()
        if not hist_df.empty:
            hist_fig.add_trace(go.Scatter(x=hist_df['time'], y=hist_df['cpu'], mode='lines', name='CPU %', line=dict(color='#00ff96')))
            hist_fig.add_trace(go.Scatter(x=hist_df['time'], y=hist_df['memory'], mode='lines', name='Memory %', line=dict(color='#00ccff')))
        else:
            hist_fig.add_annotation(text="No historical data", xref="paper", yref="paper", x=0.5, y=0.5)
        hist_fig.update_layout(template=plot_template(), height=300, title="Historical Performance Trends")
        
        return cards, cpu_fig, mem_fig, t_fig, forecast_fig, hist_fig
        
    except Exception as e:
        logger.error(f"Dashboard update error: {e}")
        return [], go.Figure(), go.Figure(), go.Figure(), go.Figure(), go.Figure()

@app.callback(
    Output("process-table-container", "children"),
    [Input("refresh-processes", "n_clicks"),
     Input("interval", "n_intervals")],
    [State("process-search", "value")]
)
def update_process_table(refresh_clicks, interval, search_term):
    """Update process table"""
    try:
        df = get_processes_full()
        anomalies = detect_anomalies(df)
        anomaly_pids = set(anomalies['pid'].tolist()) if not anomalies.empty else set()
        
        if search_term:
            df = df[df['name'].str.contains(search_term, case=False, na=False)]
        
        table_data = []
        for _, row in df.head(100).iterrows():
            is_anomaly = row['pid'] in anomaly_pids
            table_data.append({
                'PID': row['pid'],
                'Name': row['name'][:40],
                'CPU %': f"{row['cpu']:.1f}",
                'Memory (MB)': f"{row['memory_mb']:.1f}",
                'Threads': row['threads'],
                'Status': '⚠️ Anomaly' if is_anomaly else row['status'],
            })
        
        return dash_table.DataTable(
            id='process-table',
            columns=[{'name': c, 'id': c} for c in ['PID', 'Name', 'CPU %', 'Memory (MB)', 'Threads', 'Status']],
            data=table_data,
            style_cell={'textAlign': 'left', 'padding': '10px', 'fontSize': '13px', 'backgroundColor': 'rgba(20, 20, 40, 0.9)', 'color': '#e0e0ff'},
            style_data_conditional=[{'if': {'filter_query': '{Status} contains Anomaly'}, 'backgroundColor': 'rgba(255, 51, 102, 0.2)'}],
            page_size=20, sort_action="native", filter_action="native",
            style_table={'overflowX': 'auto'}
        )
    except Exception as e:
        logger.error(f"Process table error: {e}")
        return html.Div(f"Error: {str(e)}")

@app.callback(
    Output("process-action-result", "children"),
    [Input("kill-pid-btn", "n_clicks"),
     Input("term-pid-btn", "n_clicks")],
    [State("kill-pid-input", "value")]
)
def handle_process_action(kill_clicks, term_clicks, pid):
    """Handle process kill/terminate"""
    ctx = callback_context
    if not ctx.triggered or not pid:
        return html.Div()
    
    action = ctx.triggered[0]["prop_id"].split(".")[0]
    if action == "kill-pid-btn":
        success, msg = kill_process(pid)
    else:
        success, msg = terminate_process(pid)
    
    color = "#00ff96" if success else "#ff3366"
    return html.Div(msg, className="alert" if not success else "success", style={"color": color})

@app.callback(
    [Output("limits-list", "children"),
     Output("whitelist-list", "children")],
    [Input("add-limit-btn", "n_clicks"),
     Input("add-whitelist-btn", "n_clicks"),
     Input("remove-limit-btn", "n_clicks"),
     Input("remove-whitelist-btn", "n_clicks"),
     Input("interval", "n_intervals")],
    [State("limit-name", "value"),
     State("limit-cpu", "value"),
     State("limit-ram", "value"),
     State("limit-action", "value"),
     State("whitelist-name", "value"),
     State("remove-limit-name", "value"),
     State("remove-whitelist-name", "value")]
)
def update_limits(add_limit_clicks, add_whitelist_clicks, remove_limit_clicks, remove_whitelist_clicks,
                  interval, limit_name, limit_cpu, limit_ram, limit_action, whitelist_name, remove_limit_name, remove_whitelist_name):
    """Update limits display"""
    ctx = callback_context
    if ctx.triggered:
        trigger_id = ctx.triggered[0]["prop_id"].split(".")[0]
        if trigger_id == "add-limit-btn" and limit_name:
            add_limit(limit_name, limit_cpu, limit_ram, limit_action or "kill")
        elif trigger_id == "add-whitelist-btn" and whitelist_name:
            add_to_whitelist(whitelist_name)
        elif trigger_id == "remove-limit-btn" and remove_limit_name:
            remove_limit(remove_limit_name)
        elif trigger_id == "remove-whitelist-btn" and remove_whitelist_name:
            remove_from_whitelist(remove_whitelist_name)
    
    # Display limits
    limits = get_limits()
    limits_html = []
    for app, rules in limits.items():
        rules_str = []
        if rules.get("cpu"): rules_str.append(f"CPU < {rules['cpu']}%")
        if rules.get("ram"): rules_str.append(f"RAM < {rules['ram']}MB")
        limits_html.append(html.Div([
            html.Strong(app, style={"color": "#00ff96"}),
            html.Span(f" | {', '.join(rules_str)} | Action: {rules.get('action', 'kill')}", style={"marginLeft": "10px", "color": "#00ccff"}),
        ], className="alert", style={"marginBottom": "5px", "padding": "10px"}))
    
    if not limits_html:
        limits_html = [html.P("No limits configured", style={"color": "#a0a0cc"})]
    
    # Display whitelist
    whitelist = get_whitelist()
    wl_html = []
    for app in whitelist.get("apps", []):
        wl_html.append(html.Div([
            html.Span(app, style={"color": "#00ff96", "fontWeight": "bold"}),
        ], className="success", style={"padding": "8px", "marginBottom": "5px"}))
    
    if not wl_html:
        wl_html = [html.P("No whitelisted processes", style={"color": "#a0a0cc"})]
    
    return html.Div(limits_html), html.Div(wl_html)

@app.callback(
    [Output("process-distribution", "figure"),
     Output("resource-breakdown", "figure"),
     Output("analytics-stats", "children")],
    [Input("interval", "n_intervals")]
)
def update_analytics(n):
    """Update analytics"""
    try:
        df = get_processes_full()
        stats = get_system_stats()
        
        # Process Distribution
        if not df.empty:
            top_procs = df.head(10)
            dist_fig = px.pie(top_procs, values='memory_mb', names='name', title="Top 10 Processes by Memory")
        else:
            dist_fig = go.Figure()
            dist_fig.add_annotation(text="No data", xref="paper", yref="paper", x=0.5, y=0.5)
        dist_fig.update_layout(template=plot_template(), height=400)
        
        # Resource Breakdown
        breakdown_fig = go.Figure()
        breakdown_fig.add_trace(go.Bar(x=['CPU', 'Memory', 'Disk'], 
                                     y=[stats['cpu'], stats['ram_percent'], stats.get('disk_percent', 0)],
                                     marker_color=['#00ff96', '#00ccff', '#ffaa00']))
        breakdown_fig.update_layout(template=plot_template(), height=400, title="System Resource Usage")
        
        # Analytics Stats
        leaks = detect_memory_leak(df)
        anomalies = detect_anomalies(df)
        stats_html = [
            html.H3("System Insights", style={"color": "#00ccff", "marginBottom": "15px"}),
            html.P(f"Total Processes: {stats['processes']}", style={"marginBottom": "5px"}),
            html.P(f"Anomalies Detected: {len(anomalies)}", style={"marginBottom": "5px"}),
            html.P(f"Potential Memory Leaks: {len(leaks)}", style={"marginBottom": "5px"}),
            html.P(f"System Boot Time: {stats['boot_time']}", style={"marginBottom": "5px"}),
        ]
        
        return dist_fig, breakdown_fig, html.Div(stats_html)
    except Exception as e:
        logger.error(f"Analytics error: {e}")
        return go.Figure(), go.Figure(), html.Div()

@app.callback(
    Output("reports-content", "children"),
    [Input("generate-report-btn", "n_clicks"),
     Input("view-anomalies-btn", "n_clicks")]
)
def update_reports(generate_clicks, view_clicks):
    """Handle reports"""
    ctx = callback_context
    if not ctx.triggered:
        return html.Div("Select an action above", style={"color": "#a0a0cc"})
    
    action = ctx.triggered[0]["prop_id"].split(".")[0]
    if action == "generate-report-btn":
        result = generate_pdf_report()
        return html.Div([
            html.H3("PDF Report", style={"color": "#00ff96"}),
            html.P(result, style={"color": "#00ff96"})
        ])
    elif action == "view-anomalies-btn":
        anomalies = get_recent_anomalies(50)
        if anomalies:
            anomaly_list = [html.Div([
                html.Strong(f"{a['time']} - ", style={"color": "#00ff96"}),
                html.Span(a['info'], style={"color": "#e0e0ff"})
            ], className="alert", style={"marginBottom": "5px"}) for a in anomalies]
            return html.Div([
                html.H3("Recent Anomalies", style={"color": "#00ff96", "marginBottom": "15px"}),
                html.Div(anomaly_list)
            ])
        else:
            return html.Div([
                html.H3("Anomaly Log", style={"color": "#00ff96"}),
                html.P("No anomalies detected", style={"color": "#00ff96"})
            ])
    return html.Div()

@app.callback(
    [Output("status-msg", "children"),
     Output("theme-store", "data")],
    [Input("theme-btn", "n_clicks"),
     Input("pdf-btn", "n_clicks")],
    [State("theme-store", "data")]
)
def handle_buttons(theme_click, pdf_click, theme):
    """Handle theme toggle and PDF generation"""
    ctx = callback_context
    if not ctx.triggered:
        return "", theme
    
    action = ctx.triggered[0]["prop_id"].split(".")[0]
    if action == "theme-btn":
        new_theme = "light" if theme == "dark" else "dark"
        cfg = load_config()
        cfg["theme"] = new_theme
        save_config(cfg)
        return html.Div(f"🌙 Theme: {new_theme.upper()}", className="success"), new_theme
    elif action == "pdf-btn":
        result = generate_pdf_report()
        return html.Div(f"✓ {result}", className="success"), theme
    return "", theme

@app.callback(
    Output("alerts-container", "children", allow_duplicate=True),
    [Input("limit-check", "n_intervals")],
    prevent_initial_call=True
)
def check_limits(n):
    """Check and enforce limits"""
    alerts = enforce_limits()
    if alerts:
        alert_items = [html.Div(html.Strong("🔴 " + alert), className="alert") for alert in alerts[-5:]]
        return html.Div(alert_items)
    return html.Div()

# ================================================
# MAIN ENTRY POINT
# ================================================
if __name__ == '__main__':
    print("\n" + "="*60)
    print("   AI-POWERED OS PROCESS ANALYZER")
    print("   Real-time System Performance Monitor")
    print("="*60)
    print(f"\n Version: 1.0.0")
    print(f" Starting server at http://127.0.0.1:5000")
    print(f" Press Ctrl+C to stop\n")
    
    # Initialize forecast model if possible
    try:
        train_forecast_model()
    except:
        pass
    
    try:
        app.run(debug=False, port=5000, host="127.0.0.1")
    except KeyboardInterrupt:
        print("\n\nAnalyzer stopped. Goodbye!")
    except Exception as e:
        print(f"\nError: {e}")
