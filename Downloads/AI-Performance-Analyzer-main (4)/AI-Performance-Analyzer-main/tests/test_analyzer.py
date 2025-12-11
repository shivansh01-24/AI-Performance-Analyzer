import pytest

# Adjust this to your actual analyzer function
from src.analyzer import analyze_performance


def test_analyze_performance_basic_output():
    sample_metrics = {
        "cpu_usage": 40.0,
        "memory_usage": 60.0,
    }

    result = analyze_performance(sample_metrics)

    # Expect a dictionary with at least a "status" key
    assert isinstance(result, dict)
    assert "status" in result
