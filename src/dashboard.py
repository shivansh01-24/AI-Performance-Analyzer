# -*- coding: utf-8 -*-
"""
dashboard.py — CLEAN PROFESSIONAL UI VERSION
Weblytic-style | Responsive | Dynamic | Stable
"""

import dash
from dash import html, dcc, Input, Output, State, callback, callback_context
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd

from src.monitor import get_system_stats, get_processes_full, get_gpu, log_history
from src.analyzer import detect_anomalies, detect_memory_leak, get_recent_anomalies
from src.reporter import generate_pdf_report
from src.config import load_config, save_config, get_theme

# -------------------------------------------------
app = dash.Dash(__name__, title="AI OS Analyzer Pro")
app.config.suppress_callback_exceptions = True
# -------------------------------------------------

def plot_template():
    return "plotly_dark" if get_theme() == "dark" else "plotly_white"

# ======================= LAYOUT =======================
app.layout = html.Div(className="app", id="layout-wrapper", children=[

    dcc.Interval(id="interval", interval=3000, n_intervals=0),
    dcc.Store(id="theme-store", data=get_theme()),

    # -------- SIDEBAR --------
    html.Div(className="sidebar", children=[
        html.H2("AI Analyzer"),
        html.Div("Dashboard"),
        html.Div("Processes"),
        html.Div("Analytics"),
        html.Div("Reports"),
    ]),

    # -------- MAIN CONTENT --------
    html.Div(className="main", children=[

        html.H1("Dashboard"),
        html.P("Real-time OS Performance Overview"),

        html.Div([
            html.Button("Toggle Theme", id="theme-btn"),
            html.Button("Generate PDF Report", id="pdf-btn"),
            html.Div(id="status-msg")
        ]),

        # -------- METRIC CARDS --------
        html.Div(id="stats-grid", className="cards"),

        # -------- GRAPHS --------
        html.Div(className="graph-box", children=[
            html.H3("CPU Core Usage"),
            dcc.Graph(id="cpu-heatmap", config={"displayModeBar": False})
        ]),

        html.Div(className="graph-box", children=[
            html.H3("Memory Growth"),
            dcc.Graph(id="memory-growth", config={"displayModeBar": False})
        ]),

        html.Div(className="graph-box", children=[
            html.H3("Anomaly Timeline"),
            dcc.Graph(id="anomaly-timeline", config={"displayModeBar": False})
        ]),

        html.Div(className="graph-box", children=[
            html.H3("Process Tree"),
            dcc.Graph(id="process-tree", config={"displayModeBar": False})
        ]),
    ])
])

# ======================= CALLBACK =======================
@callback(
    Output("stats-grid", "children"),
    Output("cpu-heatmap", "figure"),
    Output("memory-growth", "figure"),
    Output("anomaly-timeline", "figure"),
    Output("process-tree", "figure"),
    Input("interval", "n_intervals")
)
def update_dashboard(n):
    log_history()
    stats = get_system_stats()
    df = get_processes_full()
    gpu = get_gpu()
    anomalies = detect_anomalies(df)

    gpu_load = gpu[0]["load"] if gpu else 0

    # ----- Cards -----
    cards = [
        html.Div(className="card", children=[html.H4("CPU"), html.H2(f"{stats['cpu']}%")]),
        html.Div(className="card", children=[html.H4("RAM"), html.H2(f"{stats['ram_percent']}%")]),
        html.Div(className="card", children=[html.H4("GPU"), html.H2(f"{gpu_load}%")]),
        html.Div(className="card", children=[html.H4("Processes"), html.H2(stats["processes"])]),
        html.Div(className="card", children=[html.H4("Anomalies"), html.H2(len(anomalies))]),
    ]

    # ----- CPU Heatmap -----
    cpu_fig = go.Figure(go.Heatmap(
        z=[stats["cpu_cores"]],
        colorscale="Plasma",
        showscale=False
    ))
    cpu_fig.update_layout(template=plot_template(), height=280)

    # ----- Memory Growth -----
    mem_df = df.sort_values("age_min").head(25) if not df.empty else pd.DataFrame()
    mem_fig = px.line(
        mem_df, x="age_min", y="memory_mb", color="name",
        labels={"age_min": "Age (min)", "memory_mb": "RAM (MB)"}
    )
    mem_fig.update_layout(template=plot_template())

    # ----- Timeline -----
    timeline = get_recent_anomalies()
    t_fig = go.Figure()
    if timeline:
        t_fig.add_scatter(
            x=[x["time"] for x in timeline],
            y=list(range(len(timeline))),
            mode="markers+text",
            text=[x["info"][:50] for x in timeline]
        )
    t_fig.update_layout(template=plot_template())

    # ----- Tree -----
    if not df.empty:
        df["label"] = df["name"] + " (" + df["pid"].astype(str) + ")"
        tree = px.treemap(df.head(50), path=["parent", "label"], values="memory_mb")
    else:
        tree = go.Figure()

    tree.update_layout(template=plot_template())

    return cards, cpu_fig, mem_fig, t_fig, tree

# ======================= BUTTONS =======================
@callback(
    Output("status-msg", "children"),
    Output("theme-store", "data"),
    Input("theme-btn", "n_clicks"),
    Input("pdf-btn", "n_clicks"),
    State("theme-store", "data")
)
def buttons(theme_click, pdf_click, theme):
    ctx = callback_context
    if not ctx.triggered:
        return "", theme

    action = ctx.triggered[0]["prop_id"].split(".")[0]

    if action == "theme-btn":
        new = "light" if theme == "dark" else "dark"
        cfg = load_config()
        cfg["theme"] = new
        save_config(cfg)
        return f"Theme: {new.upper()}", new

    if action == "pdf-btn":
        return generate_pdf_report(), theme

    return "", theme

# ======================= RUN =======================
if __name__ == "__main__":
    app.run(debug=False, port=5000)
