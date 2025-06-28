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
from constants import UNKNOWN_VALUE
from models.position_comparison import PositionComparison
from views.shared.team_visualizer import TeamVisualizer
from utils.utils import fix_encoding

# Configure page
st.set_page_config(
    page_title="Marmotte Flip",
    page_icon="⚔️",
    layout="wide"
)

POSITIONS = ["TOP", "JUNGLE", "MIDDLE", "BOTTOM", "UTILITY"]
POSITION_MAP = {
    "TOP": "1",
    "JUNGLE": "2", 
    "MIDDLE": "3",
    "BOTTOM": "4",
    "UTILITY": "5"
}

# Constants for display
AVG_OPPONENTS_LABEL = "Avg Opponents"

def load_team_analyzer():
    """Load and cache the team analyzer"""
    if 'team_analyzer' not in st.session_state:
        with st.spinner("Loading and analyzing team data..."):
            analyzer = TeamAnalyzer("data")
            analyzer.load_and_analyze_all_games()
            st.session_state.team_analyzer = analyzer
            st.session_state.position_comparison = PositionComparison(analyzer, None)
            st.session_state.team_visualizer = TeamVisualizer(analyzer)
            st.success("✅ Team analysis loaded successfully")
    
    return (st.session_state.team_analyzer, 
            st.session_state.position_comparison, 
            st.session_state.team_visualizer)

def display_team_overview(analyzer):
    """Display team overview and summary statistics"""
    st.subheader("🦦 Team Overview")
    
    # Get list of all Marmotte Flip players
    marmotte_players = analyzer.get_marmotte_flip_players_list()
    marmotte_players.append("Aezurly")  # Add target player
    
    st.write(f"**Marmotte Flip Team Members:** {', '.join(sorted(marmotte_players))}")
    
    # Calculate team-wide statistics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Games Analyzed", analyzer.games_analyzed)
    
    with col2:
        all_positions = analyzer.get_all_positions()
        st.metric("Positions Covered", len(all_positions))
    
    with col3:
        st.metric("Team Players", len(marmotte_players))
    
    with col4:
        # Count total individual player performances
        total_performances = 0
        for position in analyzer.our_players_stats:
            for player in analyzer.our_players_stats[position]:
                total_performances += len(analyzer.our_players_stats[position][player])
        st.metric("Total Performances", total_performances)

def display_player_detailed_analysis(analyzer):
    """Display detailed player analysis"""
    st.subheader("👤 Player Detailed Analysis")
    
    # Get all our team players
    our_players = []
    for position in POSITIONS:
        players = analyzer.get_our_players_by_position(position)
        for player in players:
            our_players.append((fix_encoding(player), position))
    
    if not our_players:
        st.warning("No team players found")
        return
    
    # Player selection
    player_options = [f"{name} ({pos})" for name, pos in our_players]
    selected_player_option = st.selectbox("Select a player to analyze:", player_options)
    
    if selected_player_option:
        # Extract player name and position
        player_name = selected_player_option.split(" (")[0]
        player_position = selected_player_option.split(" (")[1].rstrip(")")
        
        # Find the actual player name (before encoding fix)
        actual_player_name = None
        for orig_name, pos in our_players:
            if fix_encoding(orig_name) == player_name and pos == player_position:
                actual_player_name = orig_name
                break
        
        if actual_player_name:
            display_individual_player_stats(analyzer, actual_player_name, player_position)

def display_individual_player_stats(analyzer, player_name, position):
    """Display stats for an individual player"""
    
    # Get player stats using the analyzer's method
    player_stats = analyzer.get_player_average_stats(player_name, position)
    
    if not player_stats:
        st.warning(f"No stats found for {fix_encoding(player_name)} at position {position}")
        return
    
    st.write(f"**Analysis for {fix_encoding(player_name)} ({position})**")
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

def display_position_comparison(analyzer):
    """Display position comparison analysis"""
    st.subheader("⚖️ Position Comparison")
    
    # Get all our team players with their positions
    our_players_with_positions = []
    for position in POSITIONS:
        players = analyzer.get_our_players_by_position(position)
        for player in players:
            our_players_with_positions.append((fix_encoding(player), position, player))
    
    if not our_players_with_positions:
        st.warning("No team players found")
        return
    
    # Player selection dropdown
    player_options = [f"{name} ({pos})" for name, pos, _ in our_players_with_positions]
    selected_player_option = st.selectbox("Select a player to compare:", player_options)
    
    if selected_player_option:
        # Extract player info
        selected_display_name = selected_player_option.split(" (")[0]
        selected_position = selected_player_option.split(" (")[1].rstrip(")")
        
        # Find the actual player name (before encoding fix)
        actual_player_name = None
        for display_name, pos, orig_name in our_players_with_positions:
            if display_name == selected_display_name and pos == selected_position:
                actual_player_name = orig_name
                break
        
        if not actual_player_name:
            st.error("Player not found")
            return
        
        st.write(f"**Comparing {selected_display_name} vs average {selected_position} opponents**")
        
        # Display comparison data using the new model method
        try:
            # Use the team analyzer to get individual player vs opponents data with percentages
            comparison_data = analyzer.get_player_comparison_with_percentages(actual_player_name, selected_position)
            
            if comparison_data:
                # Display raw values table
                st.write("**Raw Statistics:**")
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
                
                # Create raw comparison DataFrame
                df_raw = pd.DataFrame({
                    'Metric': raw_metrics,
                    f'{selected_display_name}': [f"{val:.2f}" for val in our_raw_values],
                    AVG_OPPONENTS_LABEL: [f"{val:.2f}" for val in opponent_raw_values]
                })
                
                st.dataframe(df_raw, use_container_width=True, hide_index=True)
                
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
                
                # Create normalized radar chart
                st.write("**Performance Comparison (Percentile Ranking)**")
                create_position_radar_chart(raw_metrics, our_normalized_values, opponent_normalized_values, selected_position, selected_display_name)
                
                # Display percentage comparison table
                st.write("**Performance Percentiles (0% = worst in position, 100% = best in position):**")
                df_percentage = pd.DataFrame({
                    'Metric': raw_metrics,
                    f'{selected_display_name}': [f"{val:.1f}%" for val in our_normalized_values],
                    AVG_OPPONENTS_LABEL: [f"{val:.1f}%" for val in opponent_normalized_values]
                })
                
                st.dataframe(df_percentage, use_container_width=True, hide_index=True)
                
            else:
                st.warning("Insufficient data for position comparison")
                
        except Exception as e:
            st.error(f"Error in position comparison: {str(e)}")
            st.error(f"Debug: Player '{actual_player_name}' at position '{selected_position}'")

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
        # Load analyzers
        analyzer, _, _ = load_team_analyzer()
        
        # Main sections
        tab1, tab2, tab3 = st.tabs([
            "🏆 Team Overview", 
            "👤 Player Analysis", 
            "⚖️ Position Comparison", 
        ])
        
        with tab1:
            display_team_overview(analyzer)
        
        with tab2:
            display_player_detailed_analysis(analyzer)
        
        with tab3:
            display_position_comparison(analyzer)
            
    except Exception as e:
        st.error(f"❌ Error in team analysis: {str(e)}")
        st.info("Please check that the data directory contains valid JSON game files.")

# Run the main function
if __name__ == "__main__":
    main()
else:
    # When imported as a page, run directly
    main()
