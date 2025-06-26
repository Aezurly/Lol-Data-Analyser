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

def load_team_analyzer():
    """Load and cache the team analyzer"""
    if 'team_analyzer' not in st.session_state:
        with st.spinner("Loading and analyzing team data..."):
            analyzer = TeamAnalyzer("data")
            analyzer.load_and_analyze_all_games()
            st.session_state.team_analyzer = analyzer
            st.session_state.position_comparison = PositionComparison(analyzer, None)
            st.session_state.team_visualizer = TeamVisualizer(analyzer)
            st.success(f"✅ Team analysis loaded successfully")
    
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
        st.metric("Most Played Champion", player_stats.get('champion', 'Unknown'))

def display_position_comparison(analyzer, position_comparison):
    """Display position comparison analysis"""
    st.subheader("⚖️ Position Comparison")
    
    # Position selection
    selected_position = st.selectbox("Select position to compare:", POSITIONS)
    
    if selected_position:
        # Get our players and opponents for this position
        our_players = analyzer.get_our_players_by_position(selected_position)
        
        if not our_players:
            st.warning(f"No players found for position {selected_position}")
            return
        
        st.write(f"**Comparing {selected_position} players**")
          # Display comparison data
        try:
            # Get comparison data using available methods
            our_stats = None
            opponent_stats = analyzer.get_opponents_average_stats(selected_position)
            
            # Calculate average stats for our team at this position
            our_players = analyzer.get_our_players_by_position(selected_position)
            our_player_stats_list = []
            
            for player in our_players:
                player_stats = analyzer.get_player_average_stats(player, selected_position)
                if player_stats:
                    our_player_stats_list.append(player_stats)
              # Calculate averages for our team
            if our_player_stats_list:
                our_stats = {
                    'avg_kills': sum(stats.get('kills', 0) for stats in our_player_stats_list) / len(our_player_stats_list),
                    'avg_deaths': sum(stats.get('deaths', 0) for stats in our_player_stats_list) / len(our_player_stats_list),
                    'avg_assists': sum(stats.get('assists', 0) for stats in our_player_stats_list) / len(our_player_stats_list),
                    'avg_damage': sum(stats.get('damage', 0) for stats in our_player_stats_list) / len(our_player_stats_list),
                    'avg_cs': sum(stats.get('cs', 0) for stats in our_player_stats_list) / len(our_player_stats_list),
                    'avg_vision_score': sum(stats.get('vision_score', 0) for stats in our_player_stats_list) / len(our_player_stats_list)
                }
            
            if our_stats and opponent_stats:
                # Create comparison chart using fields that actually exist
                metrics = ['Avg Kills', 'Avg Deaths', 'Avg Assists', 'Avg Damage', 'Avg CS', 'Avg Vision']
                our_values = [
                    our_stats.get('avg_kills', 0),
                    our_stats.get('avg_deaths', 0),
                    our_stats.get('avg_assists', 0),
                    our_stats.get('avg_damage', 0),
                    our_stats.get('avg_cs', 0),
                    our_stats.get('avg_vision_score', 0)
                ]
                opponent_values = [
                    opponent_stats.get('kills', 0),
                    opponent_stats.get('deaths', 0),
                    opponent_stats.get('assists', 0),
                    opponent_stats.get('damage', 0),
                    opponent_stats.get('cs', 0),
                    opponent_stats.get('vision_score', 0)
                ]
                
                # Create comparison DataFrame
                df_comparison = pd.DataFrame({
                    'Metric': metrics,
                    'Our Team': our_values,
                    'Opponents': opponent_values
                })
                
                # Display table
                st.dataframe(df_comparison, use_container_width=True, hide_index=True)
                
                # Create radar chart
                create_position_radar_chart(metrics, our_values, opponent_values, selected_position)
                
            else:
                st.warning("Insufficient data for position comparison")
                
        except Exception as e:
            st.error(f"Error in position comparison: {str(e)}")

def create_position_radar_chart(metrics, our_values, opponent_values, position):
    """Create a radar chart for position comparison"""
    
    # Normalize values to 0-100 scale for better visualization
    all_values = our_values + opponent_values
    if max(all_values) > 0:
        our_normalized = [(val / max(all_values)) * 100 for val in our_values]
        opp_normalized = [(val / max(all_values)) * 100 for val in opponent_values]
    else:
        our_normalized = [0] * len(our_values)
        opp_normalized = [0] * len(opponent_values)
    
    fig = go.Figure()
    
    # Add our team trace
    fig.add_trace(go.Scatterpolar(
        r=our_normalized + [our_normalized[0]],  # Close the polygon
        theta=metrics + [metrics[0]],
        fill='toself',
        name='Our Team',
        fillcolor='rgba(52, 152, 219, 0.2)',
        line=dict(color='rgba(52, 152, 219, 1)', width=2)
    ))
    
    # Add opponents trace
    fig.add_trace(go.Scatterpolar(
        r=opp_normalized + [opp_normalized[0]],  # Close the polygon
        theta=metrics + [metrics[0]],
        fill='toself',
        name='Opponents',
        fillcolor='rgba(231, 76, 60, 0.2)',
        line=dict(color='rgba(231, 76, 60, 1)', width=2)
    ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 100]
            )
        ),
        showlegend=True,
        title=f"Position Comparison: {position}",
        height=500
    )
    
    st.plotly_chart(fig, use_container_width=True)

def display_team_vs_opponents_radar(team_visualizer):
    """Display team vs opponents radar chart"""
    st.subheader("🕸️ Team vs Opponents Radar Chart")
    
    try:
        # This would need to be implemented in the team_visualizer
        # For now, show a placeholder
        st.info("Radar chart functionality will be implemented with the team visualizer")
        
        # Create a sample radar chart structure
        metrics = ['Kills', 'Deaths', 'Assists', 'Damage', 'Gold', 'Vision']
        
        st.write("**Radar Chart Options:**")
        chart_type = st.selectbox(
            "Select chart type:",
            ["Overall Team Performance", "By Position", "By Game"]
        )
        
        if chart_type == "Overall Team Performance":
            st.info("Overall team performance radar chart would be displayed here")
        elif chart_type == "By Position":
            position = st.selectbox("Select position:", POSITIONS)
            st.info(f"Position-specific radar chart for {position} would be displayed here")
        elif chart_type == "By Game":
            st.info("Game-by-game radar chart would be displayed here")
            
    except Exception as e:
        st.error(f"Error creating radar chart: {str(e)}")

def main():
    """Main team analysis page"""
    st.title("🦦 Team Analysis")
    st.write("Marmotte Flip vs Opponents Analysis")
    
    try:
        # Load analyzers
        analyzer, position_comparison, team_visualizer = load_team_analyzer()
        
        # Main sections
        tab1, tab2, tab3, tab4 = st.tabs([
            "🏆 Team Overview", 
            "👤 Player Analysis", 
            "⚖️ Position Comparison", 
            "🕸️ Radar Charts"
        ])
        
        with tab1:
            display_team_overview(analyzer)
        
        with tab2:
            display_player_detailed_analysis(analyzer)
        
        with tab3:
            display_position_comparison(analyzer, position_comparison)
        
        with tab4:
            display_team_vs_opponents_radar(team_visualizer)
            
    except Exception as e:
        st.error(f"❌ Error in team analysis: {str(e)}")
        st.info("Please check that the data directory contains valid JSON game files.")

# Run the main function
if __name__ == "__main__":
    main()
else:
    # When imported as a page, run directly
    main()
