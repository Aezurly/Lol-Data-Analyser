# CONSTANTS: Application constants and configuration values
"""
Constants used throughout the LoL Data Analyzer application
"""

# Standard position names (as they appear in JSON data)
POSITION_FULL_NAMES = {
    "TOP": "TOP",
    "JUNGLE": "JUNGLE", 
    "MIDDLE": "MIDDLE",
    "BOTTOM": "BOTTOM",
    "UTILITY": "SUPPORT"  # UTILITY from JSON becomes SUPPORT in our app
}

# Short position names (3 characters max)
POSITION_SHORT_NAMES = {
    "TOP": "TOP",
    "JUNGLE": "JGL",
    "MIDDLE": "MID", 
    "BOTTOM": "BOT",
    "SUPPORT": "SUP"
}

# All valid positions in our system (full names)
POSITIONS = ["TOP", "JUNGLE", "MIDDLE", "BOTTOM", "SUPPORT"]

# Position mappings for numeric input
POSITION_MAP = {
    "TOP": "1",
    "JUNGLE": "2", 
    "MIDDLE": "3",
    "BOTTOM": "4",
    "SUPPORT": "5"
}

# Base URLs for position icons
_TOP_ICON_URL = 'https://wiki.leagueoflegends.com/en-us/images/Top_icon.png?58442'
_JUNGLE_ICON_URL = 'https://wiki.leagueoflegends.com/en-us/images/Jungle_icon.png?9225d'
_MIDDLE_ICON_URL = 'https://wiki.leagueoflegends.com/en-us/images/Middle_icon.png?fa3f0'
_BOTTOM_ICON_URL = 'https://wiki.leagueoflegends.com/en-us/images/Bottom_icon.png?6d4b2'
_SUPPORT_ICON_URL = 'https://wiki.leagueoflegends.com/en-us/images/Support_icon.png?af1ff'

# Position icon URLs from League of Legends Wiki
POSITION_ICON_URLS = {
    'TOP': _TOP_ICON_URL,
    'JUNGLE': _JUNGLE_ICON_URL, 
    'MIDDLE': _MIDDLE_ICON_URL,
    'BOTTOM': _BOTTOM_ICON_URL,
    'SUPPORT': _SUPPORT_ICON_URL,
    # Legacy and alternative mappings for backward compatibility
    'UTILITY': _SUPPORT_ICON_URL,
    'ADC': _BOTTOM_ICON_URL,
    'MID': _MIDDLE_ICON_URL,
    'JGL': _JUNGLE_ICON_URL,
    'BOT': _BOTTOM_ICON_URL,
    'SUP': _SUPPORT_ICON_URL,
}

# Default icon for unknown positions
DEFAULT_POSITION_ICON_URL = 'https://wiki.leagueoflegends.com/en-us/images/All_roles_icon.png?d9e6c'

# Team colors for charts
TEAM_COLORS = {
    'Team 1': '#3498db',  # Blue
    'Team 2': '#e74c3c'   # Red
}

# Team names
TEAM_1_NAME = "🔵 Blue Side"
TEAM_2_NAME = "🔴 Red Side"

# Team simple names (without emojis)
TEAM_1_SIMPLE = "Blue"
TEAM_2_SIMPLE = "Red"

# Team emojis
TEAM_1_EMOJI = "🔵"
TEAM_2_EMOJI = "🔴"

# Game result emojis
WIN_EMOJI = "🏆"
LOSE_EMOJI = "💀"

# Page paths for navigation
PAGES = {
    'HOME': "⚔️_LoL_Data_Analyzer.py",
    'SINGLE_GAME': "pages/1_📊_Single_Game.py",
    'GLOBAL_STATS': "pages/2_🌌_Global_Stats.py", 
    'MARMOTTE_FLIP': "pages/3_🦦_Marmotte_Flip.py",
    'PLAYER_PROFILE': "pages/4_👤_Player_Profile.py"
}

# Data directory
DATA_DIR = "data"

# Team IDs used in the data
TEAM_1_ID = "100"
TEAM_2_ID = "200"

# UI Labels
TEAM_1_LABEL = "Team 1"
TEAM_2_LABEL = "Team 2"

# Common values
UNKNOWN_VALUE = "Unknown"

# Target player for team analysis
TARGET_PLAYER = "Aezurly"
