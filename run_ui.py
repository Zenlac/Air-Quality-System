#!/usr/bin/env python3
"""
Air Pollution Forecasting System - UI Launcher
Simple script to launch the Streamlit web interface

Author: Air Quality Commission
Created: 2026-02-27
"""

import subprocess
import sys
import os

def main():
    """Launch the Streamlit UI"""
    print("Starting Air Pollution Forecasting System Web UI...")
    print("=" * 60)
    
    # Check if streamlit is installed
    try:
        import streamlit
        print(f"Streamlit version: {streamlit.__version__}")
    except ImportError:
        print("Streamlit not found. Please install it with:")
        print("pip install streamlit>=1.28.0")
        sys.exit(1)
    
    # Launch the app
    try:
        app_path = os.path.join(os.path.dirname(__file__), 'app.py')
        print(f"Launching web interface from: {app_path}")
        print("=" * 60)
        print("The web interface will open in your default browser")
        print("If not opened automatically, visit: http://localhost:8501")
        print("Press Ctrl+C in this terminal to stop the server")
        print("=" * 60)
        
        # Run streamlit
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", app_path,
            "--server.port", "8501",
            "--server.address", "localhost",
            "--browser.gatherUsageStats", "false"
        ])
        
    except KeyboardInterrupt:
        print("\nShutting down web interface...")
    except Exception as e:
        print(f"Error launching web interface: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
