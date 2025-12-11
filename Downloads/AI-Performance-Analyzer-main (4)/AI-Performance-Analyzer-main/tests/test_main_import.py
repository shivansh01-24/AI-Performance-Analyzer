def test_main_imports():
    """
    This test just ensures that main.py can be imported
    without executing any long-running code or crashing.
    """
    import importlib

    module = importlib.import_module("main")
    assert module is not None
