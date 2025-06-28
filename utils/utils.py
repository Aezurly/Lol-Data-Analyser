# UTILITY: Shared utilities for console setup and text encoding
import sys
from rich.console import Console
from colorama import init

def setup_console():
    """Initialize console with proper encoding and colorama"""
    # Initialize colorama for Windows compatibility
    init(autoreset=True)
    
    # Create console instance
    console = Console()
    
    # Configure UTF-8 encoding for Windows
    if sys.platform == "win32":
        sys.stdout.reconfigure(encoding='utf-8')
    
    return console


def fix_encoding(text):
    """Fix encoding issues in text (convert from Latin-1 to UTF-8)"""
    if not isinstance(text, str):
        return text
    try:
        return text.encode('latin-1').decode('utf-8')
    except (UnicodeDecodeError, UnicodeEncodeError):
        try:
            return text.encode('windows-1252').decode('utf-8')
        except (UnicodeDecodeError, UnicodeEncodeError):
            return text


def normalize_player_name(name):
    """Normalize player name for consistent storage and comparison"""
    if not isinstance(name, str):
        return name

    fixed_name = fix_encoding(name)

    import unicodedata
    normalized_name = unicodedata.normalize('NFC', fixed_name)
    
    return normalized_name