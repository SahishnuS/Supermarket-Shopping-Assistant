"""
Entry point to run the Customer Chat Interface.
Usage: python run_customer.py
"""
import subprocess
import sys
import os

if __name__ == "__main__":
    app_path = os.path.join(os.path.dirname(__file__), "app", "customer.py")
    subprocess.run([
        sys.executable, "-m", "streamlit", "run", app_path,
        "--server.port", "8502",
        "--server.headless", "true",
        "--theme.base", "dark"
    ])
