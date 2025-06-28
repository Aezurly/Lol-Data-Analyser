# VIEW: Multi-game analysis page for Streamlit interface  
"""
Multi-game analysis page - replicates terminal multi-game functionality
Displays player rankings, statistics, and search functionality
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Import models and utilities
from models.multi_game_analyzer import MultiGameAnalyzer
from utils.utils import fix_encoding, normalize_player_name, get_position_display_name
from utils.predicates import (
    has_minimum_games, 
    has_sufficient_position_players,
    MetricFormatter, 
    RankCalculator,
    DataFrameStyler,
    DisplayHelpers,
    ValidationHelpers
)
from constants import DATA_DIR, POSITIONS
from views.streamlit.components.navigation import create_navigation

# Configure page
st.set_page_config(
    page_title="Global Stats",
    page_icon="⚔️",
    layout="wide"
)

def load_multi_game_analyzer():
    """Load and cache the multi-game analyzer"""
    if 'multi_game_analyzer' not in st.session_state:
        with st.spinner("Loading and analyzing all games..."):
            analyzer = MultiGameAnalyzer(DATA_DIR)
            analyzer.load_all_games()
            st.session_state.multi_game_analyzer = analyzer
            st.success(f"✅ Loaded {analyzer.games_analyzed} games successfully")
    
    return st.session_state.multi_game_analyzer

def display_player_rankings(analyzer):
    """Display player rankings table using model methods"""
    st.subheader("📋 Player Table")
    
    # Use model method to get formatted player data
    player_stats = analyzer.create_player_rankings_data()
    
    if not player_stats:
        st.warning("No player data available")
        return pd.DataFrame()
    
    df = pd.DataFrame(player_stats)
    
    # Sort options using utility helper
    sort_options = DisplayHelpers.get_sort_options()
    sort_by = st.selectbox(
        "Sort by:",
        sort_options,
        key="player_rankings_sort"    
    )
    
    df_sorted = df.sort_values(sort_by, ascending=False)
    
    # Display table with column configuration from utility
    column_config = DataFrameStyler.get_win_rate_column_config()
    st.dataframe(
        df_sorted, 
        use_container_width=True, 
        hide_index=True,
        column_config=column_config
    )
    
    return df_sorted

def apply_dataframe_styling(df):
    """Apply color styling to the comparison DataFrame using utility classes"""
    return DataFrameStyler.apply_comparison_styling(df)

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
    styled_df = apply_dataframe_styling(comparison_df)
    
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

def display_champions_table(analyzer, player_name):
    """Display the champions played table using model methods"""
    champions_data = analyzer.get_player_champions_data(player_name)
    
    if not champions_data:
        return
        
    st.write("**Champions Played:**")
    champions_df = pd.DataFrame(champions_data).sort_values('Games', ascending=False)
    st.dataframe(champions_df, use_container_width=True, hide_index=True)

def display_player_detailed_stats(analyzer, player_name):
    """Display detailed stats for a specific player using model methods"""
    if not ValidationHelpers.validate_player_exists(analyzer, player_name):
        st.error(f"No stats found for {player_name}")
        return
    
    stats = analyzer.player_stats.get(player_name)
    
    # Display all sections using updated functions
    display_summary_metrics(analyzer, player_name)
    display_detailed_metrics(analyzer, player_name)
    
    # Position comparison
    st.write("**📊 Position Comparison:**")
    display_position_comparison(analyzer, stats)
    
    # Champions table
    display_champions_table(analyzer, player_name)

def display_champion_analytics(analyzer):
    """Display champion analytics using model methods"""
    st.subheader("🎯 Champion Analytics")
    
    # Get champion analytics from model
    all_champions = analyzer.get_champion_analytics()
    
    # Validate champions data
    if not ValidationHelpers.validate_champions_data(all_champions):
        st.warning("No champion data available")
        return
    
    # Display note about feature
    st.info("📊 Champion analytics feature coming soon!")
    st.write("This feature requires individual game data which is not currently stored in the PlayerStats objects.")
    
    # Show champions played by each player
    st.write("**Champions Played by Players:**")
    
    # Display champion information using model data
    for champion, players in sorted(all_champions.items()):
        with st.expander(f"🎭 {champion}"):
            for player in players:
                st.write(f"• {player}")

def main():
    """Main multi-game analysis page using model methods and utilities"""
    create_navigation("Global Stats")
    
    st.title("🌌 Global Stats")
    st.write("Analyze performance across multiple games")
    
    # Add cache clear button
    if st.button("🔄 Reload Data", help="Clear cache and reload all game data"):
        if 'multi_game_analyzer' in st.session_state:
            del st.session_state.multi_game_analyzer
        st.rerun()
    
    try:
        # Load analyzer
        analyzer = load_multi_game_analyzer()
        
        # Validate games analyzed using utility
        if not ValidationHelpers.validate_games_analyzed(analyzer):
            st.error("❌ No games were successfully analyzed")
            st.info("Please check that there are valid JSON game files in the data directory")
            return
        
        # Display summary
        st.success(f"📊 Analyzing {analyzer.games_analyzed} games")
        
        # Main sections using display helpers
        tab1, tab2 = st.tabs(["📋 Player Table", "🎯 Champion Analytics"])
        
        with tab1:
            display_player_rankings(analyzer)
        
        with tab2:
            display_champion_analytics(analyzer)
            
    except Exception as e:
        st.error(f"❌ Error in multi-game analysis: {str(e)}")
        st.info("Please check that the data directory contains valid JSON game files.")

# Run the main function directly when imported as a page
main()
