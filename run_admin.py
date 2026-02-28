"""
Entry point to run the Admin Panel.
Usage: python run_admin.py
"""
import subprocess
import sys
import os

if __name__ == "__main__":
    app_path = os.path.join(os.path.dirname(__file__), "app", "admin.py")
    subprocess.run([
        sys.executable, "-m", "streamlit", "run", app_path,
        "--server.port", "8501",
        "--server.headless", "true",
        "--theme.base", "dark"
    ])
