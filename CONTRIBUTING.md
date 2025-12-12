# Contributing to AI Performance Analyzer

Thank you for your interest in contributing!  
We welcome contributions of all kinds: bug fixes, new features, documentation improvements, performance optimizations, or even just helping with issues.

### Table of Contents
- [Code of Conduct](#code-of-conduct)
- [How to Contribute](#how-to-contribute)
- [Development Setup](#development-setup)
- [Pull Request Guidelines](#pull-request-guidelines)
- [Commit Message Conventions](#commit-message-conventions)
- [Reporting Issues](#reporting-issues)
- [Questions?](#questions)

### Code of Conduct
This project follows the [Contributor Covenant Code of Conduct](https://www.contributor-covenant.org/version/2/1/code_of_conduct/).  
Please be respectful and professional in all interactions.

### How to Contribute
1. Fork the repository
2. Create a new branch from `main`:
   ```bash
   git checkout -b feature/your-feature-name
   # or
   git checkout -b fix/bug-description

Make your changes
Commit with clear messages (see conventions below)
Push your branch and open a Pull Request (PR)

Development Setup
Bash# Clone the repo
git clone https://github.com/shivansh01-24/AI-Performance-Analyzer.git
cd AI-Performance-Analyzer

# Create and activate virtual environment
python -m venv venv
venv\Scripts\activate    # Windows
# source venv/bin/activate  # Linux/macOS

# Install dependencies
pip install -r requirements.txt

# (Optional) Install dev tools
pip install black flake8 pytest
Pull Request Guidelines

PRs must target the main branch
Include a clear description of what the PR does
Add or update tests when changing core logic
Ensure all tests pass (pytest)
Format code with Black (black .)
Lint code (flake8)
Update documentation (README, CHANGELOG, etc.) when needed
Use one PR per feature/fix

Commit Message Conventions
We use the Conventional Commits specification:
text<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
Types: feat, fix, docs, style, refactor, perf, test, chore, ci
Examples:
textfeat: add process-specific anomaly detection
fix: handle missing psutil metrics gracefully
docs: update installation instructions
refactor: simplify dashboard layout logic
Reporting Issues

Use the issue templates (bug report / feature request)
Include steps to reproduce (if it's a bug)
Mention your OS, Python version, and any relevant logs

Questions?
Feel free to open an issue with the question label, or reach out via GitHub Discussions.
Thank you for helping make AI Performance Analyzer better!
textJust create the file `CONTRIBUTING.md` in your repo root, paste the entire content above, commit, and push.



# Project Contributors

This project has been collaboratively developed by the following team members.  
All contributors have participated equally in the design, development, and refinement of the project.

---

## Team Members

### 1. Shivansh Srivastava
- Core team member  
- Contributed to project development and implementation

### 2. Aditya Singh
- Core team member  
- Contributed to project development and implementation

### 3. Naman Gupta
- Core team member  
- Contributed to project development and implementation

---

We acknowledge the collective effort, collaboration, and commitment of all team members throughout the development of this project.

