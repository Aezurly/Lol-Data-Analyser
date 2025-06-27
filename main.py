# CONTROLLER: Main entry point that coordinates application startup
"""
League of Legends Game Analysis Tool

Supports both terminal and web (Streamlit) interfaces for analyzing 
League of Legends game data with visualizations and statistics.
"""

import sys
import subprocess
from config import INTERFACE_MODE, InterfaceMode

def main():
    """Main entry point for the game analysis application"""
    print(f"Starting LoL Data Analyzer in {INTERFACE_MODE.value} mode...")
    
    if INTERFACE_MODE == InterfaceMode.STREAMLIT:
        # Launch Streamlit application
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", 
            "views/streamlit/streamlit_app.py",
            "--server.port=8501",
            "--server.runOnSave=true",
            "--server.fileWatcherType=auto"
        ])
    else:
        # Launch terminal application
        from controllers.terminal.app_controller import AppController
        app = AppController()
        app.run()

if __name__ == "__main__":
    main()