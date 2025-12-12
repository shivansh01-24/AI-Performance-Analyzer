# 🤖 AI-Powered OS Process Analyzer

<div align="center">

[![Python 3.8+](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![PRs Welcome](https://img.shields.io/badge/PRs-Welcome-brightgreen.svg)](CONTRIBUTING.md)
[![Status](https://img.shields.io/badge/Status-Active-success.svg)](README.md)

**A Professional AI-Driven System Performance Monitor with Real-Time Anomaly Detection**

[Features](#-features) • [Quick Start](#-quick-start) • [Installation](#-installation) • [Documentation](#-documentation) • [Team](#-team)

</div>

---

## 🌟 Features

### Core Capabilities
- ✅ **Real-Time OS Monitoring** - CPU, Memory, Disk I/O, Network metrics
- 🤖 **AI Anomaly Detection** - Isolation Forest-based intelligent detection
- 📊 **Interactive Dashboard** - Modern, responsive web interface
- 🎨 **Dark/Light Theme** - Professional theming system
- 📄 **PDF Report Generation** - Executive summaries with charts
- 🎯 **Process Management** - Auto-kill, suspend, and resource limiting
- 💻 **GPU Monitoring** - Real-time GPU metrics and temperature
- 📈 **Performance Analytics** - Historical trends and predictions
- 🔄 **Auto-Refresh** - 3-second interval updates
- 📱 **Fully Responsive** - Works on desktop, tablet, mobile

### Advanced Features
- **Memory Leak Detection** - Identifies suspicious memory patterns
- **Bottleneck Analysis** - CPU, Memory, Disk, Network optimization
- **Process Tree Visualization** - Hierarchical process relationships
- **System Optimization Suggestions** - AI-powered recommendations
- **User Whitelist System** - Protect critical processes
- **Resource Limit Enforcement** - Set thresholds for applications
- **Activity Logging** - Complete audit trail of all actions

---

## 🚀 Quick Start

```bash
# 1. Clone the repository
git clone https://github.com/yourusername/AI-Performance-Analyzer.git
cd AI-Performance-Analyzer

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run the application
python main.py

# 4. Open in browser
# Navigate to: http://127.0.0.1:5000
```

---
## 📸 OUTPUT
<img width="945" height="541" alt="image" src="https://github.com/user-attachments/assets/d458108d-cf43-4586-b915-c9381ec67420" />

<img width="945" height="501" alt="image" src="https://github.com/user-attachments/assets/29a86c3b-bba3-4e93-bacb-5ed97fa43701" />




## 📦 Installation

### System Requirements
- **Python**: 3.8 or higher
- **OS**: Windows 10+, macOS 10.14+, Ubuntu 18.04+
- **RAM**: 2GB minimum (4GB recommended)

### Step-by-Step Installation

#### 1. Clone Repository
```bash
git clone https://github.com/yourusername/AI-Performance-Analyzer.git
cd "AI-Performance-Analyzer"
```

#### 2. Create Virtual Environment (Recommended)
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

#### 3. Install Dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

#### 4. Run Application
```bash
python main.py
```

#### 5. Access Dashboard
Open your browser and go to: **http://127.0.0.1:5000**

---

## 📖 Documentation

### Project Structure
```
AI-Performance-Analyzer/
├── main.py                    # Entry point
├── requirements.txt           # Dependencies
├── VERSION                    # Version file
├── README.md                  # This file
├── CONTRIBUTING.md            # Contributing guidelines
├── src/
│   ├── __init__.py           # Package initializer
│   ├── analyzer.py           # AI anomaly detection
│   ├── dashboard.py          # Dash web interface
│   ├── monitor.py            # System monitoring
│   ├── reporter.py           # PDF report generation
│   ├── config.py             # Configuration management
│   ├── limit_manager.py      # Resource limit enforcement
│   ├── logger.py             # Logging setup
│   ├── model.py              # ML models
│   └── utils.py              # Utility functions
├── data/
│   ├── config.json           # User settings
│   ├── history.csv           # Historical metrics
│   └── user_limits.json      # Resource limits
├── assets/
│   └── style.css             # Dashboard styling
├── logs/
│   └── app.log               # Application logs
├── reports/
│   └── *.pdf                 # Generated reports
└── tests/
    ├── test_analyzer.py
    ├── test_monitor.py
    ├── test_model.py
    ├── test_integration_pipeline.py
    └── test_main_import.py
```

### Key Modules

#### `analyzer.py`
Handles AI anomaly detection and analysis:
- `detect_anomalies()` - Isolation Forest-based detection
- `detect_memory_leak()` - Memory pattern analysis
- `detect_bottlenecks()` - Resource bottleneck detection
- `get_recent_anomalies()` - Anomaly history

#### `monitor.py`
Real-time system monitoring:
- `get_system_stats()` - CPU, Memory, Process counts
- `get_processes_full()` - Detailed process information
- `get_gpu()` - GPU metrics (NVIDIA)
- `safe_action()` - Process control (kill, suspend, etc.)

#### `dashboard.py`
Interactive web interface (Dash/Plotly):
- Real-time metric cards
- CPU heatmap visualization
- Memory growth timeline
- Anomaly detection timeline
- Process tree visualization
- Theme toggle and PDF generation

#### `reporter.py`
PDF report generation using ReportLab:
- System summary
- Top processes by memory
- Anomaly reports
- Memory leak analysis
- Executive summary

#### `config.py`
Configuration management:
- Theme persistence (dark/light)
- Auto-refresh interval settings
- PDF report settings
- User preferences

---

## 🎯 Usage Examples

### Start the Dashboard
```bash
python main.py
```
Server runs on `http://127.0.0.1:5000`

### Generate PDF Report
Click "PDF Report" button in dashboard or:
```python
from src.reporter import generate_pdf_report
report = generate_pdf_report()
```

### Detect Anomalies Programmatically
```python
from src.monitor import get_processes_full
from src.analyzer import detect_anomalies

df = get_processes_full()
anomalies = detect_anomalies(df)
print(f"Found {len(anomalies)} anomalies")
```

### Set Resource Limits
```python
from src.limit_manager import add_limit

add_limit("chrome.exe", cpu=50, ram=1024, time=60, action="kill")
```

### Monitor System Stats
```python
from src.monitor import get_system_stats, get_gpu

stats = get_system_stats()
print(f"CPU: {stats['cpu']}%")
print(f"RAM: {stats['ram_percent']}%")

gpu = get_gpu()
if gpu:
    print(f"GPU: {gpu[0]['load']}%")
```

---

## 🧪 Testing

### Run Tests
```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_analyzer.py -v

# Run with coverage
pytest --cov=src tests/
```

### Run Individual Module Tests
```bash
# Test analyzer module
python -m pytest tests/test_analyzer.py -v

# Test monitor module
python -m pytest tests/test_monitor.py -v

# Test integration
python -m pytest tests/test_integration_pipeline.py -v
```

---

## 🎨 Dashboard Features

### Real-Time Metrics
- **CPU Usage** - Current CPU utilization percentage
- **RAM Usage** - Memory consumption with total available
- **GPU Load** - NVIDIA GPU metrics (if available)
- **Running Processes** - Active process count
- **Anomalies Detected** - AI-detected abnormalities
- **System Health** - Overall system status

### Interactive Visualizations
- **CPU Heatmap** - Per-core CPU usage visualization
- **Memory Timeline** - Top processes memory growth
- **Anomaly Timeline** - Historical anomaly markers
- **Process Tree** - Memory distribution across processes

### Controls
- **Toggle Theme** - Switch between dark and light modes
- **Generate PDF** - Export comprehensive report
- **Auto-Refresh** - 3-second update interval
- **Real-time Updates** - Live dashboard data

---

## 🛠️ Configuration

### config.json
```json
{
    "theme": "dark",
    "auto_start_monitoring": true,
    "refresh_interval_sec": 3,
    "pdf_report_auto_save": true
}
```

### user_limits.json
```json
{
    "chrome": {"cpu": 80, "ram": 2048, "time": 120, "action": "kill"},
    "java": {"cpu": 70, "ram": 1024, "time": 60, "action": "suspend"}
}
```

### whitelist.json
```json
{
    "apps": ["svchost.exe", "csrss.exe", "System"]
}
```

---

## 👥 Team

This project is developed by a team of 3 members working on system performance monitoring and AI integration.

| Contribution Area | Focus |
|-------------------|-------|
| **Core Architecture** | System monitoring, AI integration |
| **Frontend/UI** | Dashboard design, responsiveness |
| **Backend/Reporting** | Data analysis, PDF generation |

---

## 🤝 Contributing

We welcome contributions! Please read [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

### How to Contribute
1. **Fork** the repository
2. **Create** a feature branch (`git checkout -b feature/AmazingFeature`)
3. **Commit** changes (`git commit -m 'Add AmazingFeature'`)
4. **Push** to branch (`git push origin feature/AmazingFeature`)
5. **Open** a Pull Request

### Development Setup
```bash
# Install dev dependencies
pip install -r requirements.txt
pip install pytest pytest-cov pytest-mock

# Run tests before submitting PR
pytest --cov=src tests/
```

---

## 📋 Requirements

See `requirements.txt`:
- **psutil** - System monitoring
- **pandas** - Data analysis
- **scikit-learn** - Anomaly detection
- **dash** - Web framework
- **plotly** - Visualizations
- **reportlab** - PDF generation
- **flask** - Web server
- **pytest** - Testing framework

---

## 🐛 Troubleshooting

### Port 5000 Already in Use
```bash
# Change port in main.py
app.run(port=5001)
```

### GPU Not Detected
- Install NVIDIA drivers and CUDA
- Install GPUtil: `pip install GPUtil`

### Permission Denied (Process Control)
- Run as Administrator (Windows) or `sudo` (Linux/Mac)

### High CPU Usage
- Increase refresh interval in config.json
- Reduce process monitoring frequency

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🌐 Links

- **Issues**: [GitHub Issues](https://github.com/yourusername/AI-Performance-Analyzer/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/AI-Performance-Analyzer/discussions)
- **Releases**: [GitHub Releases](https://github.com/yourusername/AI-Performance-Analyzer/releases)

---

## 📞 Support

Need help? 

- 📖 Check the [Documentation](#-documentation)
- 🐛 Search [Existing Issues](https://github.com/yourusername/AI-Performance-Analyzer/issues)
- 💬 Start a [Discussion](https://github.com/yourusername/AI-Performance-Analyzer/discussions)
- 📧 Contact the team

---

<div align="center">

Made with ❤️ by the AI Performance Analyzer Team

**⭐ Star us on GitHub if you like this project!**

</div>


Contributors
Name	Contribution Summary
Shivansh Srivastava	Core team member and contributor to the project development
Aditya Singh	Core team member and contributor to the project development
Naman Gupta	Core team member and contributor to the project development
