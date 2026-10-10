"""Unified Runner for SMT Engineering Workspace.

Starts the combined local host server hosting:
1. Pathway LMS Frontend Dashboard (at / and /lms)
2. LMS Multi-tab UI Viewer (at /lms/lms_ui_viewer.html)
3. Crucible Proctored Sandbox Engine (at /lobby/1, /exam, /result, /path)
4. Sandbox Backend API & Runner (at /api/*)

Usage:
    python run_localhost.py
"""
import sys
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent

def main():
    print("=" * 65)
    print("STARTING UNIFIED LOCALHOST (LMS + SANDBOX COMBINED)")
    print("=" * 65)
    print("  * LMS Frontend Path:      http://127.0.0.1:8000/")
    print("  * LMS Multi-Tab Viewer:   http://127.0.0.1:8000/lms/lms_ui_viewer.html")
    print("  * Sandbox Exam Engine:    http://127.0.0.1:8000/sandbox")
    print("  * Sandbox API & Health:   http://127.0.0.1:8000/api/health")
    print("=" * 65)
    print("Starting server on http://127.0.0.1:8000 ...")
    sys.stdout.flush()

    serve_py = ROOT / "product" / "entrypoints" / "http-api" / "serve.py"
    subprocess.run([sys.executable, str(serve_py)], check=True)

if __name__ == "__main__":
    main()
