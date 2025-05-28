"""
League of Legends Game Analysis Tool

A command-line application for analyzing League of Legends game data.
Supports both single game analysis with visualizations and multi-game 
analysis with player statistics and leaderboards.
"""

from app_controller import AppController

def main():
    """Main entry point for the game analysis application"""
    app = AppController()
    app.run()

if __name__ == "__main__":
    main()