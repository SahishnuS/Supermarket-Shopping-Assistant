"""
Entry point to run the Flask API server.
Usage: python run_api.py
"""
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from backend.api import app

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
