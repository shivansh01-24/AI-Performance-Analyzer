import numpy as np
import pytest

# Adjust this import to your actual class/function
from src.model import PerformanceModel


def test_model_can_be_instantiated():
    model = PerformanceModel()
    assert model is not None


def test_model_predict_returns_output():
    model = PerformanceModel()

    # Example: assuming the model takes [cpu_usage, memory_usage]
    X = np.array([[50.0, 70.0]])

    prediction = model.predict(X)

    # We don't assume a specific value, just that something comes back
    assert prediction is not None
