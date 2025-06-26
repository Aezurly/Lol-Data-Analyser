import os
from enum import Enum

class InterfaceMode(Enum):
    TERMINAL = "terminal"
    STREAMLIT = "streamlit"

# Feature flag - peut être défini par variable d'environnement
INTERFACE_MODE = InterfaceMode.STREAMLIT

# Autres configurations
DATA_DIRECTORY = "data"
TARGET_PLAYER = "Aezurly"

# Configuration Streamlit
STREAMLIT_CONFIG = {
    'page_title': 'LoL Data Analyzer',
    'page_icon': '⚔️',
    'layout': 'wide',
    'initial_sidebar_state': 'expanded'
}

# Application metadata
APP_VERSION = "1.0.0"
APP_DESCRIPTION = "League of Legends Game Analysis Tool"
