# COMPONENT: Player card display component
"""
Reusable player card component for displaying player information
"""

import streamlit as st
from utils.utils import fix_encoding, normalize_player_name, get_position_display_name
from constants import PAGES, WIN_EMOJI, LOSE_EMOJI


def display_player_card(player_name: str, player_stats=None, participant=None, show_profile_button: bool = True):
    profile_clicked = False

    if participant:
        extra_title = participant.get_champion()
        games_text = get_position_display_name(participant.get_position(), short=True)
        extra_info = f"{participant.get_kills()}/{participant.get_deaths()}/{participant.get_assists()}"
    elif player_stats:
        extra_title = get_position_display_name(player_stats.get_most_played_position(), short=True)
        win_rate = player_stats.get_win_rate() * 100
        games_text = f"{player_stats.games_played} games"
        extra_info = f"{win_rate:.1f}% win rate"
    else:
        extra_title = "Unknown"
        games_text = "No data"
        extra_info = ""
    
    # Use normalized player name for display
    display_name = normalize_player_name(player_name)
    
    with st.container(border=True):
        st.markdown(f"##### {display_name} - *{extra_title}*")
        if participant:
            st.write(f"{games_text} • {WIN_EMOJI if participant.get_win() else LOSE_EMOJI} • {extra_info}")
        else:
            st.caption(f"{games_text} • {extra_info}")
        
        if show_profile_button:
            if st.button("View Profile", key=f"profile_{player_name}", use_container_width=True):
                st.session_state.selected_player = normalize_player_name(player_name)
                st.switch_page(PAGES['PLAYER_PROFILE'])
                profile_clicked = True
    
    return profile_clicked


def display_player_cards_grid(matching_players: list, analyzer, cols_per_row: int = 3, show_profile_buttons: bool = True):
    """Display a grid of player cards using multi-game stats"""
    for i in range(0, len(matching_players), cols_per_row):
        cols = st.columns(cols_per_row)
        
        for j, player_name in enumerate(matching_players[i:i+cols_per_row]):
            with cols[j]:
                # Get basic player info
                player_stats = analyzer.player_stats.get(player_name)
                if player_stats:
                    display_player_card(player_name, player_stats=player_stats, show_profile_button=show_profile_buttons)


def display_participants_cards_grid(participants: list, cols_per_row: int = 5, show_profile_buttons: bool = False):
    """Display a grid of participant cards using single game data"""
    for i in range(0, len(participants), cols_per_row):
        cols = st.columns(cols_per_row)
        
        for j, participant in enumerate(participants[i:i+cols_per_row]):
            with cols[j]:
                player_name = participant.get_name()
                display_player_card(player_name, participant=participant, show_profile_button=show_profile_buttons)


def display_player_search_results(search_term: str, analyzer):
    """
    Display search results for players
    
    Args:
        search_term: The search term used
        analyzer: MultiGameAnalyzer instance
    """
    # Search for players
    matching_players = analyzer.search_players(search_term)
    
    if matching_players:
        st.caption(f"Found {len(matching_players)} matching player(s)")
        display_player_cards_grid(matching_players, analyzer)
    else:
        st.warning(f"No players found matching '{search_term}'")
