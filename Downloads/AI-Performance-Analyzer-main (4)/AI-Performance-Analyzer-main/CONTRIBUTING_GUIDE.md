# 🤝 Contributing to AI Performance Analyzer

First off, thank you for considering contributing to AI Performance Analyzer! It's people like you that make AI Performance Analyzer such a great tool.

## Code of Conduct

This project and everyone participating in it is governed by a Code of Conduct. By participating, you are expected to uphold this code.

---

## How Can I Contribute?

### Reporting Bugs

Before creating bug reports, please check the issue list as you might find out that you don't need to create one. When you are creating a bug report, please include as many details as possible:

* **Use a clear and descriptive title**
* **Describe the exact steps which reproduce the problem**
* **Provide specific examples to demonstrate the steps**
* **Describe the behavior you observed after following the steps**
* **Explain which behavior you expected to see instead and why**
* **Include screenshots and animated GIFs if possible**
* **Include your OS version and Python version**

### Suggesting Enhancements

Enhancement suggestions are tracked as GitHub issues. When creating an enhancement suggestion, please include:

* **Use a clear and descriptive title**
* **Provide a step-by-step description of the suggested enhancement**
* **Provide specific examples to demonstrate the steps**
* **Describe the current behavior and the expected behavior**
* **Explain why this enhancement would be useful**

### Pull Requests

* Fill in the required template
* Follow the Python styleguides
* End all files with a newline
* Avoid platform-dependent code

---

## Development Setup

### 1. Fork and Clone
```bash
git clone https://github.com/yourusername/AI-Performance-Analyzer.git
cd AI-Performance-Analyzer
```

### 2. Create Virtual Environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
pip install pytest pytest-cov pytest-mock flake8 black
```

### 4. Create Feature Branch
```bash
git checkout -b feature/your-feature-name
```

---

## Making Changes

### Code Style

We follow PEP 8 with some modifications:

```python
# Good
def calculate_metrics(data, threshold=0.8):
    """Calculate performance metrics."""
    results = []
    for item in data:
        if item > threshold:
            results.append(item)
    return results

# Bad
def calc(d,t=0.8):
    r=[]
    for i in d:
        if i>t:r.append(i)
    return r
```

### Formatting

```bash
# Format code with black
black src/ tests/

# Check style with flake8
flake8 src/ tests/

# Run type checking
mypy src/ --ignore-missing-imports
```

### Docstrings

```python
def detect_anomalies(df: pd.DataFrame) -> pd.DataFrame:
    """
    Detect anomalies in process data using Isolation Forest.
    
    Args:
        df: DataFrame with process metrics
        
    Returns:
        DataFrame with anomalies and scores
        
    Raises:
        ValueError: If DataFrame is empty
        
    Example:
        >>> df = get_processes_full()
        >>> anomalies = detect_anomalies(df)
    """
```

---

## Testing

### Write Tests

```python
# tests/test_analyzer.py
import pytest
from src.analyzer import detect_anomalies
from src.monitor import get_processes_full

def test_detect_anomalies_empty_dataframe():
    """Test anomaly detection with empty DataFrame."""
    import pandas as pd
    df = pd.DataFrame()
    result = detect_anomalies(df)
    assert result.empty

def test_detect_anomalies_with_data():
    """Test anomaly detection with real data."""
    df = get_processes_full()
    if not df.empty:
        anomalies = detect_anomalies(df)
        assert isinstance(anomalies, pd.DataFrame)
```

### Run Tests

```bash
# Run all tests
pytest -v

# Run specific test
pytest tests/test_analyzer.py::test_detect_anomalies -v

# Run with coverage
pytest --cov=src --cov-report=html tests/
```

---

## Committing Changes

### Commit Messages

```
Short (50 char or less) summary of changes

More detailed explanatory text, if necessary. Wrap it to about 72
characters or so. In some contexts, the first line is treated as
the subject of an email and the rest of the text as the body.

- Bullet point 1
- Bullet point 2
- Bullet point 3

Fixes #123
```

### Examples

```
Add anomaly detection to dashboard

- Implement Isolation Forest algorithm
- Add UI components for anomaly display
- Add tests for edge cases

Fixes #45
```

---

## Submitting Changes

### Before Submitting

- [ ] Code follows style guidelines
- [ ] All tests pass: `pytest`
- [ ] Code is formatted: `black src/ tests/`
- [ ] No linting issues: `flake8 src/ tests/`
- [ ] Docstrings added
- [ ] Tests added for new code
- [ ] Commit messages are clear

### GitHub PR Process

1. Push your feature branch
2. Create a Pull Request against `main`
3. Fill in the PR template completely
4. Ensure CI/CD checks pass
5. Request review from maintainers

### PR Template

```markdown
## Description
Brief description of changes

## Related Issues
Fixes #123

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Documentation update
- [ ] Performance improvement

## Testing
- [ ] Unit tests added/updated
- [ ] Tested on Windows/Mac/Linux
- [ ] Manual testing completed

## Checklist
- [ ] Code follows style guidelines
- [ ] Tests pass locally
- [ ] Docstrings added
```

---

## Documentation

### Updating Documentation

- Update README.md for user-facing changes
- Update docstrings for code changes
- Add examples for new features
- Keep CHANGELOG.md updated

### Documentation Style

```markdown
# Heading 1
## Heading 2
### Heading 3

**Bold text** and *italic text*

- Bullet point
- Another point

\`\`\`python
# Code block
code_example()
\`\`\`

> Quote or note
```

---

## Project Structure Guidelines

```
src/
├── analyzer.py          # AI/ML logic
├── dashboard.py         # Web interface
├── monitor.py           # System monitoring
├── reporter.py          # Report generation
├── config.py            # Configuration
├── logger.py            # Logging setup
└── utils.py             # Helper functions

tests/
├── test_analyzer.py
├── test_monitor.py
├── test_dashboard.py
└── test_integration_pipeline.py
```

---

## Questions?

- Check existing issues
- Review documentation
- Start a discussion
- Email the maintainers

---

## Recognition

Contributors will be recognized in:
- CONTRIBUTORS.md
- README.md
- GitHub profiles

---

## License

By contributing, you agree that your contributions will be licensed under its MIT License.

---

<div align="center">

**Thank you for contributing! 🎉**

</div>
