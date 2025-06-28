from constants import POSITION_FULL_NAMES, POSITION_SHORT_NAMES


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


def normalize_position(position_raw):
    """Normalize position name to standard format (SUPPORT instead of UTILITY)"""
    if not isinstance(position_raw, str):
        return position_raw
    
    # Convert to uppercase for consistency
    position_upper = position_raw.upper().strip()
    
    # Use the mapping from constants to convert UTILITY -> SUPPORT
    return POSITION_FULL_NAMES.get(position_upper, position_upper)


def get_position_display_name(position, short=False):
    """Get display name for position (short or full format)"""
    if not isinstance(position, str):
        return position
    
    # First normalize the position
    normalized_position = normalize_position(position)
    
    if short:
        return POSITION_SHORT_NAMES.get(normalized_position, normalized_position)
    else:
        return normalized_position


def get_team_players_summary(team_analyzer):
    """Get a summary of all team players with their primary positions"""
    team_players = {}
    
    for position in ["TOP", "JUNGLE", "MIDDLE", "BOTTOM", "SUPPORT"]:
        players = team_analyzer.get_our_players_by_position(position)
        if players:
            team_players[position] = [normalize_player_name(player) for player in players]
    
    return team_players