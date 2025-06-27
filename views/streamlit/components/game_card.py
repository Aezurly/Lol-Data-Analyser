# COMPONENT: Game card display component
"""
Reusable game card component for displaying game information
"""

import streamlit as st
import pandas as pd
from utils.utils import fix_encoding


def display_game_card(game_summary: dict, analyzer=None):
    analyze_clicked = False
    
    with st.container(border=True):
        st.markdown(f"**{game_summary['date_string']}** • {game_summary['duration']}")
        
        # Prepare team data for table
        max_players = max(
            len(game_summary['team1_players_with_champions']), 
            len(game_summary['team2_players_with_champions'])
        )
        
        # Fill shorter team with empty strings
        team1_display = [
            fix_encoding(player_champion) 
            for player_champion in game_summary['team1_players_with_champions']
        ]
        team2_display = [
            fix_encoding(player_champion) 
            for player_champion in game_summary['team2_players_with_champions']
        ]
        
        while len(team1_display) < max_players:
            team1_display.append("")
        while len(team2_display) < max_players:
            team2_display.append("")
        
        # Create DataFrame
        team_data = pd.DataFrame({
            f"🔵 Blue {'🏆' if game_summary['winning_team'] == 1 else ''}": team1_display,
            f"🔴 Red {'🏆' if game_summary['winning_team'] == 2 else ''}": team2_display
        })
        
        st.dataframe(team_data, hide_index=True, use_container_width=True)
        
        # Button to view detailed game analysis (if analyzer provided)
        if analyzer:
            if st.button("See More", key=f"game_{game_summary['filename']}", use_container_width=True):
                st.session_state.selected_game = game_summary['file_path']
                st.switch_page("pages/1_📊_Single_Game.py")
                analyze_clicked = True
    
    return analyze_clicked


def display_game_cards_grid(games_data: list, analyzer, cols_per_row: int = 2):
    for i in range(0, len(games_data), cols_per_row):
        cols = st.columns(cols_per_row)
        
        for j, game_info in enumerate(games_data[i:i+cols_per_row]):
            with cols[j]:
                game_summary = analyzer.get_game_summary_for_display(game_info)
                display_game_card(game_summary, analyzer)
