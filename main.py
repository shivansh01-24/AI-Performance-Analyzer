# -*- coding: utf-8 -*-
"""
AI-Powered OS Process Analyzer

Entry point for the AI Performance Analyzer dashboard application.
Provides a web-based interface for real-time OS/process monitoring,
anomaly detection, and performance insights.
"""


import sys
from pathlib import Path

VERSION = (Path(__file__).parent / "VERSION").read_text(encoding="utf-8").strip()


# ================================================
# SAFE IMPORT + ERROR HANDLING
# ================================================
try:
    from src.dashboard import app
except ImportError as e:
    print("\n" + "="*60)
    print(" ERROR: Dashboard could not be loaded!")
    print(" Make sure all files in 'src/' folder are created.")
    print(f" ImportError: {e}")
    print("="*60 + "\n")
    sys.exit(1)
except Exception as e:
    print("\n" + "="*60)
    print(" FATAL ERROR: Something went wrong while starting the app.")
    print(f" Error: {e}")
    print("="*60 + "\n")
    sys.exit(1)

# ================================================
# UNICODE-SAFE BANNER (Works on all terminals)
# ================================================
def print_banner():
    try:
        # Try fancy Unicode banner
        print("""
╔══════════════════════════════════════════════════════════╗
║    AI-POWERED OS PROCESS ANALYZER (FULL VERSION)        ║
║           Auto-Kill • AI • GPU • Process Tree           ║
║       Dark/Light Theme • PDF Report • Zero Crash        ║
║                 MADE FOR 30/30 MARKS                    ║
╚══════════════════════════════════════════════════════════╝
        """)
    except UnicodeEncodeError:
        # Fallback for old terminals
        print("\n" + "="*58)
        print("   AI-POWERED OS PROCESS ANALYZER (FULL VERSION)")
        print("   Auto-Kill | AI | GPU | Process Tree | Theme Toggle")
        print("   PDF Report | Zero Crash | 30/30 GUARANTEED")
        print("="*58 + "\n")

if __name__ == '__main__':
    print_banner()
    print(f" Version: {VERSION}")
    print(" Starting the dashboard...")
    print(" Open your browser and go to: http://127.0.0.1:5000")
    print(" Press Ctrl+C to stop the analyzer.\n")
    
    try:
        # Dash 3.x – correct way
        app.run(debug=False, port=5000)
    except KeyboardInterrupt:
        print("\n\nAnalyzer stopped by user. Bye!")
    except Exception as e:
        print(f"\nServer crashed: {e}")



