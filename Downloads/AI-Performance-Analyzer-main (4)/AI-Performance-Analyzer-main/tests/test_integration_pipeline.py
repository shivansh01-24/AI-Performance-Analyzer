import pytest

from src.data_collection import collect_system_metrics
from src.analyzer import analyze_performance
from src.model import PerformanceModel


def test_full_pipeline_runs_without_errors():
    # 1. collect metrics
    metrics = collect_system_metrics()
    assert isinstance(metrics, dict)

    # 2. analyze performance
    analysis = analyze_performance(metrics)
    assert analysis is not None

    # 3. model prediction using collected metrics
    model = PerformanceModel()
    cpu = metrics.get("cpu_usage", 0.0)
    mem = metrics.get("memory_usage", 0.0)

    prediction = model.predict([[cpu, mem]])

    assert prediction is not None
