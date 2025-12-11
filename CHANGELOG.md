# Changelog

All notable changes to **AI Performance Analyzer** are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),  
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2025-12-11
### Added
- Initial public release
- Modular version with full project structure
- SingleFile-Version (ultra-lightweight one-file implementation)
- Real-time CPU, memory, disk & process monitoring
- AI-powered anomaly detection using Isolation Forest
- Interactive web dashboard (Dash + Plotly)
- Docker & docker-compose support
- Centralized rotating logging
- Comprehensive documentation and single-file READMEs
- CONTRIBUTING.md and professional open-source setup

### Fixed
- Graceful handling of missing system metrics

## [0.2.0] - Unreleased (Planned Q1 2026)
### Added
- Process-specific anomaly alerts with detailed breakdown
- Export performance reports (CSV / PDF)
- Email & Slack notification hooks
- Dark/Light theme toggle in dashboard
- Config file support (`config.yaml`)
- Improved mobile-responsive dashboard

### Changed
- Optimized data buffer size for lower memory usage
- Better anomaly scoring visualization

## [0.3.0] - Unreleased (Planned Q2 2026)
### Added
- Predictive forecasting using LSTM neural network
- Multi-system / remote host monitoring (agent mode)
- REST API endpoints for integration
- Custom alert rules engine
- Plugin system for extended metrics
- Health check endpoint

### Security
- Input validation on API routes

## [1.0.0] - Unreleased (Planned Q3 2026)
### Added
- Full production-ready stability
- Official Docker image on Docker Hub
- Cloud deployment guides (AWS, GCP, Azure)
- Community plugin marketplace
- Full documentation site (ai-performance-analyzer.io)
- Authentication & user roles (admin/viewer)

### Changed
- Complete refactor for async performance
- Switch to FastAPI + WebSockets for real-time updates

### Removed
- Legacy synchronous dashboard routes
