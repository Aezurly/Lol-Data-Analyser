# COMPONENT: Player card display component
"""
Reusable player card component for displaying player information
"""

import streamlit as st
from utils.utils import fix_encoding


def display_player_card(player_name: str, player_stats, show_profile_button: bool = True):
    profile_clicked = False
    
    with st.container(border=True):
        st.markdown(f"**{fix_encoding(player_name)}** • {player_stats.get_most_played_position()}")
        st.caption(f"{player_stats.games_played} games • {player_stats.get_win_rate()*100:.1f}%")
        
        if show_profile_button:
            if st.button("View Profile", key=f"profile_{player_name}", use_container_width=True):
                st.session_state.selected_player = player_name
                st.switch_page("pages/4_👤_Player_Profile.py")
                profile_clicked = True
    
    return profile_clicked


def display_player_cards_grid(matching_players: list, analyzer, cols_per_row: int = 3, show_profile_buttons: bool = True):
    for i in range(0, len(matching_players), cols_per_row):
        cols = st.columns(cols_per_row)
        
        for j, player_name in enumerate(matching_players[i:i+cols_per_row]):
            with cols[j]:
                # Get basic player info
                player_stats = analyzer.player_stats.get(player_name)
                if player_stats:
                    display_player_card(player_name, player_stats, show_profile_buttons)


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
