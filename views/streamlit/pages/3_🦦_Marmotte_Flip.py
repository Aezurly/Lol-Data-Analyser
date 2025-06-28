# VIEW: Team analysis page for Streamlit interface
"""
Team analysis page - replicates terminal team analysis functionality
Displays Marmotte Flip team vs opponents analysis, radar charts, position comparison
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np

# Import models and utilities
from models.team_analyzer import TeamAnalyzer
from models.team_service import TeamService
from constants import UNKNOWN_VALUE, POSITIONS
from models.position_comparison import PositionComparison
from views.shared.team_visualizer import TeamVisualizer
from utils.utils import fix_encoding, get_position_display_name, normalize_player_name

# Configure page
st.set_page_config(
    page_title="Marmotte Flip",
    page_icon="⚔️",
    layout="wide"
)

# Constants for display
AVG_OPPONENTS_LABEL = "Avg Opponents"

def load_team_analyzer():
    """Load and cache the team analyzer with service layer"""
    if 'team_analyzer' not in st.session_state:
        with st.spinner("Loading and analyzing team data..."):
            analyzer = TeamAnalyzer("data")
            analyzer.load_and_analyze_all_games()
            st.session_state.team_analyzer = analyzer
            st.session_state.team_service = TeamService(analyzer)
            st.session_state.position_comparison = PositionComparison(analyzer, None)
            st.session_state.team_visualizer = TeamVisualizer(analyzer)
            st.success("✅ Team analysis loaded successfully")
    
    return (st.session_state.team_analyzer, 
            st.session_state.team_service,
            st.session_state.position_comparison, 
            st.session_state.team_visualizer)

def display_team_overview(team_service: TeamService):
    """Display team overview and summary statistics"""
    st.subheader("🦦 Team Overview")
    
    # Get team players using service
    marmotte_players = team_service.get_marmotte_flip_players()
    team_stats = team_service.get_team_summary_stats()
    
    st.write(f"**Marmotte Flip Team Members:** {', '.join(sorted(marmotte_players))}")
    
    # Display statistics using centralized service
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Games Analyzed", team_stats.get('games_analyzed', 0))
    
    with col2:
        st.metric("Positions Covered", team_stats.get('positions_covered', 0))
    
    with col3:
        st.metric("Team Players", team_stats.get('total_players', 0))
    
    with col4:
        st.metric("Total Performances", team_stats.get('total_performances', 0))

def display_player_detailed_analysis(team_service: TeamService, analyzer):
    """Display detailed player analysis using team service"""
    st.subheader("👤 Player Detailed Analysis")
    
    # Get player options from service
    player_options = team_service.get_player_options_for_ui()
    
    if not player_options:
        st.warning("No team players found")
        return
    
    # Player selection using formatted options
    display_options = [display_name for display_name, _, _ in player_options]
    selected_option = st.selectbox("Select a player to analyze:", display_options)
    
    if selected_option:
        # Find the selected player data
        for display_name, position, original_name in player_options:
            if display_name == selected_option:
                display_individual_player_stats(analyzer, original_name, position, team_service)
                break

def display_individual_player_stats(analyzer, player_name, position, team_service: TeamService):
    """Display stats for an individual player"""
    
    # Get player stats using the analyzer's method
    player_stats = analyzer.get_player_average_stats(player_name, position)
    
    if not player_stats:
        formatted_name = team_service.format_player_name_for_display(player_name)
        formatted_position = team_service.get_position_display_name(position)
        st.warning(f"No stats found for {formatted_name} at position {formatted_position}")
        return
    
    formatted_name = team_service.format_player_name_for_display(player_name)
    formatted_position = team_service.get_position_display_name(position)
    
    st.write(f"**Analysis for {formatted_name} ({formatted_position})**")
    st.write(f"Games played: {player_stats.get('games_played', 0)}")
    
    # Display stats in columns
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Avg Kills", f"{player_stats.get('kills', 0):.1f}")
        st.metric("Avg Deaths", f"{player_stats.get('deaths', 0):.1f}")
        st.metric("Avg Assists", f"{player_stats.get('assists', 0):.1f}")
    
    with col2:
        st.metric("Avg Damage", f"{player_stats.get('damage', 0):.0f}")
        st.metric("Avg CS", f"{player_stats.get('cs', 0):.1f}")
        st.metric("CS/min", f"{player_stats.get('cs_per_minute', 0):.1f}")
    
    with col3:
        st.metric("Avg KDA", f"{player_stats.get('kda', 0):.2f}")
        st.metric("Vision Score", f"{player_stats.get('vision_score', 0):.1f}")
        st.metric("Most Played Champion", player_stats.get('champion', UNKNOWN_VALUE))

def display_position_comparison(team_service: TeamService, analyzer):
    """Display position comparison analysis using team service"""
    st.subheader("⚖️ Position Comparison")
    
    # Get player options from service
    player_options = team_service.get_player_options_for_ui()
    
    if not player_options:
        st.warning("No team players found")
        return
    
    # Player selection using formatted options
    display_options = [display_name for display_name, _, _ in player_options]
    selected_option = st.selectbox("Select a player to compare:", display_options, key="position_comparison")
    
    if selected_option:
        # Find the selected player data
        for display_name, position, original_name in player_options:
            if display_name == selected_option:
                _display_player_comparison(analyzer, original_name, position, team_service)
                break

def _display_player_comparison(analyzer, player_name, position, team_service: TeamService):
    """Display comparison for a specific player"""
    formatted_name = team_service.format_player_name_for_display(player_name)
    formatted_position = team_service.get_position_display_name(position)
    
    st.info(f"Comparing **{formatted_name}** vs average {formatted_position} opponents", icon="📄")
    
    # Display comparison data using the analyzer method
    try:
        # Use the team analyzer to get individual player vs opponents data with percentages
        comparison_data = analyzer.get_player_comparison_with_percentages(player_name, position)
        
        if comparison_data:
            _display_comparison_tables_and_chart(comparison_data, formatted_name, formatted_position)
        else:
            st.warning("Insufficient data for position comparison")
            
    except Exception as e:
        st.error(f"Error in position comparison: {str(e)}")
        st.error(f"Debug: Player '{player_name}' at position '{position}'")

def _display_comparison_tables_and_chart(comparison_data, player_name, position):
    """Display comparison tables and radar chart"""
    # Display raw values table
    raw_metrics = ['Kills', 'Deaths', 'Assists', 'Dmg/min', 'CS/min', 'Vision/min', 'KDA']
    our_raw_values = [
        comparison_data['our_stats_raw']['kills'],
        comparison_data['our_stats_raw']['deaths'],
        comparison_data['our_stats_raw']['assists'],
        comparison_data['our_stats_raw']['damage_per_minute'],
        comparison_data['our_stats_raw']['cs_per_minute'],
        comparison_data['our_stats_raw']['vision_per_minute'],
        comparison_data['our_stats_raw']['kda']
    ]
    opponent_raw_values = [
        comparison_data['opponent_stats_raw']['kills'],
        comparison_data['opponent_stats_raw']['deaths'],
        comparison_data['opponent_stats_raw']['assists'],
        comparison_data['opponent_stats_raw']['damage_per_minute'],
        comparison_data['opponent_stats_raw']['cs_per_minute'],
        comparison_data['opponent_stats_raw']['vision_per_minute'],
        comparison_data['opponent_stats_raw']['kda']
    ]
    
    # Get normalized percentages for radar chart
    our_normalized_values = [
        comparison_data['our_stats_normalized'].get('kills', 0),
        comparison_data['our_stats_normalized'].get('deaths', 0),
        comparison_data['our_stats_normalized'].get('assists', 0),
        comparison_data['our_stats_normalized'].get('damage_per_minute', 0),
        comparison_data['our_stats_normalized'].get('cs_per_minute', 0),
        comparison_data['our_stats_normalized'].get('vision_per_minute', 0),
        comparison_data['our_stats_normalized'].get('kda', 0)
    ]
    opponent_normalized_values = [
        comparison_data['opponent_stats_normalized'].get('kills', 0),
        comparison_data['opponent_stats_normalized'].get('deaths', 0),
        comparison_data['opponent_stats_normalized'].get('assists', 0),
        comparison_data['opponent_stats_normalized'].get('damage_per_minute', 0),
        comparison_data['opponent_stats_normalized'].get('cs_per_minute', 0),
        comparison_data['opponent_stats_normalized'].get('vision_per_minute', 0),
        comparison_data['opponent_stats_normalized'].get('kda', 0)
    ]

    create_position_radar_chart(raw_metrics, our_normalized_values, opponent_normalized_values, position, player_name)
    
    # Create combined comparison table with raw stats and percentiles
    st.write("**Performance Comparison:**")
    df_combined = pd.DataFrame({
        'Metric': raw_metrics,
        f'{player_name} (Raw)': [f"{val:.2f}" for val in our_raw_values],
        f'{player_name} (%)': [f"{val:.1f}%" for val in our_normalized_values],
        f'{AVG_OPPONENTS_LABEL} (Raw)': [f"{val:.2f}" for val in opponent_raw_values],
        f'{AVG_OPPONENTS_LABEL} (%)': [f"{val:.1f}%" for val in opponent_normalized_values]
    })
    
    st.dataframe(df_combined, use_container_width=True, hide_index=True)
    st.caption("Raw values show actual statistics. Percentiles show performance ranking (0% = worst in position, 100% = best in position)")


def create_position_radar_chart(metrics, our_values, opponent_values, position, player_name=None):
    """Create a radar chart for position comparison using normalized percentage values"""
    
    # The values are already normalized to 0-100 percentages from the model
    fig = go.Figure()
    
    # Use player name if provided, otherwise use "Our Team"
    our_label = player_name if player_name else "Our Team"
    
    # Add our team trace
    fig.add_trace(go.Scatterpolar(
        r=our_values + [our_values[0]],  # Close the polygon
        theta=metrics + [metrics[0]],
        fill='toself',
        name=our_label,
        fillcolor='rgba(52, 152, 219, 0.2)',
        line={'color': 'rgba(52, 152, 219, 1)', 'width': 2}
    ))
    
    # Add opponents trace
    fig.add_trace(go.Scatterpolar(
        r=opponent_values + [opponent_values[0]],  # Close the polygon
        theta=metrics + [metrics[0]],
        fill='toself',
        name=AVG_OPPONENTS_LABEL,
        fillcolor='rgba(231, 76, 60, 0.2)',
        line={'color': 'rgba(231, 76, 60, 1)', 'width': 2}
    ))
    
    fig.update_layout(
        polar={
            'radialaxis': {
                'visible': True,
                'range': [0, 100],
                'ticksuffix': '%'
            }
        },
        showlegend=True,
        title=f"Position Comparison: {position} (Normalized Percentiles)",
        height=500
    )
    
    st.plotly_chart(fig, use_container_width=True)

def main():
    """Main team analysis page"""
    st.title("🦦 Team Analysis")
    st.write("Marmotte Flip vs Opponents Analysis")
    
    try:
        # Load analyzers and service
        analyzer, team_service, _, _ = load_team_analyzer()
        
        # Main sections
        tab1, tab2, tab3 = st.tabs([
            "🏆 Team Overview", 
            "👤 Player Analysis", 
            "⚖️ Position Comparison", 
        ])
        
        with tab1:
            display_team_overview(team_service)
        
        with tab2:
            display_player_detailed_analysis(team_service, analyzer)
        
        with tab3:
            display_position_comparison(team_service, analyzer)
            
    except Exception as e:
        st.error(f"❌ Error in team analysis: {str(e)}")
        st.info("Please check that the data directory contains valid JSON game files.")

# Run the main function
if __name__ == "__main__":
    main()
else:
    # When imported as a page, run directly
    main()
