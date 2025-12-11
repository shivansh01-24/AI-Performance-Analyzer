import pytest

# Adjust this import if your module path is different
from src.data_collection import collect_system_metrics


def test_collect_system_metrics_returns_dict():
    metrics = collect_system_metrics()

    # Basic type & key checks
    assert isinstance(metrics, dict)
    assert "cpu_usage" in metrics
    assert "memory_usage" in metrics


def test_collect_system_metrics_value_ranges():
    metrics = collect_system_metrics()

    cpu = metrics["cpu_usage"]
    mem = metrics["memory_usage"]

    # CPU and memory should be between 0 and 100
    assert 0 <= cpu <= 100
    assert 0 <= mem <= 100
