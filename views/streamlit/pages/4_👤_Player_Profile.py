# VIEW: Player Profile page for Streamlit interface
"""
Player Profile page - displays detailed statistics for a selected player
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Import models and utilities
from models.multi_game_analyzer import MultiGameAnalyzer
from utils.utils import fix_encoding, normalize_player_name, get_position_display_name
from utils.predicates import (
    DataFrameStyler,
    DisplayHelpers,
    ValidationHelpers
)
from constants import PAGES, POSITIONS

# Configure page
st.set_page_config(
    page_title="Player Profile",
    page_icon="👤",
    layout="wide"
)

def load_multi_game_analyzer():
    """Load and cache the multi-game analyzer"""
    if 'multi_game_analyzer' not in st.session_state:
        with st.spinner("Loading and analyzing all games..."):
            analyzer = MultiGameAnalyzer("data")
            analyzer.load_all_games()
            st.session_state.multi_game_analyzer = analyzer
    
    return st.session_state.multi_game_analyzer

def display_summary_metrics(analyzer, player_name):
    """Display the summary metrics in columns using model methods"""
    metrics = analyzer.get_player_summary_metrics(player_name)
    if not metrics:
        st.error("No metrics available")
        return
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Games Played", metrics['games_played'])
    
    with col2:
        st.metric("Position", metrics['position'])
    
    with col3:
        st.metric("Most Played Champion", metrics['most_played_champion'])
    
    with col4:
        st.metric("Avg KDA", f"{metrics['avg_kda']:.2f}")

def display_detailed_metrics(analyzer, player_name):
    """Display detailed statistics in columns using model methods"""
    metrics = analyzer.get_player_detailed_metrics(player_name)
    if not metrics:
        st.error("No detailed metrics available")
        return
    
    st.write("**Detailed Statistics:**")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Dmg/min", f"{metrics['dmg_per_min']:.1f}")
        st.metric("CS/min", f"{metrics['cs_per_min']:.1f}")
    
    with col2:
        st.metric("Vision/min", f"{metrics['vision_per_min']:.2f}")
        st.metric("DMG/Gold", f"{metrics['dmg_per_gold']:.2f}")
    
    with col3:
        st.metric("Total Kills", metrics['total_kills'])
        st.metric("Total Deaths", metrics['total_deaths'])

def display_position_comparison(analyzer, player_stats):
    """Display position-based comparison statistics using model methods"""
    position = player_stats.get_most_played_position()
    
    # Use model method to check if sufficient players
    if not analyzer.has_sufficient_players_for_comparison(player_stats.name):
        st.info(f"Not enough players in {position} position for comparison")
        return
    
    # Create comparison data using model method
    comparison_data = analyzer.create_position_comparison_data(player_stats.name)
    
    if not comparison_data:
        st.warning("Unable to generate comparison data")
        return
    
    # Create and style DataFrame using utility methods
    comparison_df = pd.DataFrame(comparison_data)
    styled_df = DataFrameStyler.apply_comparison_styling(comparison_df)
    
    # Get position players count for display message
    position_players = analyzer.get_players_by_position(position)
    message = DisplayHelpers.format_position_comparison_message(position, len(position_players))
    
    # Display the comparison
    st.write(message)
    column_config = DataFrameStyler.get_comparison_column_config()
    st.dataframe(
        styled_df, 
        use_container_width=True, 
        hide_index=True,
        column_config=column_config
    )

def display_champions_table(analyzer, player_name):
    """Display the champions played table using model methods"""
    champions_data = analyzer.get_player_champions_data(player_name)
    
    if not champions_data:
        return
        
    st.write("**Champions Played:**")
    champions_df = pd.DataFrame(champions_data).sort_values('Games', ascending=False)
    st.dataframe(champions_df, use_container_width=True, hide_index=True)

def main():
    """Main player profile page"""
    # Check if a player has been selected
    if 'selected_player' not in st.session_state:
        st.title("👤 Player Profile")
        st.warning("No player selected. Please go back to the home page and search for a player.")
        if st.button("🏠 Go to Home Page"):
            st.switch_page(PAGES['HOME'])
        return
    
    # Normalize the player name from session state for consistent lookup
    player_name = normalize_player_name(st.session_state.selected_player)
    
    try:
        # Load analyzer
        analyzer = load_multi_game_analyzer()
        
        player_exists = ValidationHelpers.validate_player_exists(analyzer, player_name)
        if not player_exists:
            original_name = st.session_state.selected_player
            player_exists = ValidationHelpers.validate_player_exists(analyzer, original_name)
            if player_exists:
                player_name = original_name
        
        if not player_exists:
            st.error(f"Player '{player_name}' not found in the data")
            st.info("Available players (sample):")
            all_players = analyzer.get_all_players()
            if all_players:
                st.write(", ".join(all_players)) 
            if st.button("🏠 Go to Home Page"):
                st.switch_page(PAGES['HOME'])
            return
        
        # Get player stats
        player_stats = analyzer.player_stats.get(player_name)
        
        # Header with player name
        st.title(f"👤 {fix_encoding(player_name)}")
        st.subheader("Player Profile & Statistics")
        
        # Navigation buttons
        col1, col2, col3 = st.columns([1, 1, 2])
        with col1:
            if st.button("🏠 Home"):
                st.switch_page(PAGES['HOME'])
        with col2:
            if st.button("🌌 Global Stats"):
                st.switch_page(PAGES['GLOBAL_STATS'])
        
        # Summary metrics
        st.header("📊 Summary")
        display_summary_metrics(analyzer, player_name)
        
        # Detailed metrics
        st.header("📈 Detailed Statistics")
        display_detailed_metrics(analyzer, player_name)
        
        # Position comparison
        st.header("🎯 Position Comparison")
        display_position_comparison(analyzer, player_stats)
        
        # Champions table
        st.header("🎭 Champions")
        display_champions_table(analyzer, player_name)
        
    except Exception as e:
        st.error(f"❌ Error loading player profile: {str(e)}")
        if st.button("🏠 Go to Home Page"):
            st.switch_page(PAGES['HOME'])

# Run the main function directly when imported as a page
main()
