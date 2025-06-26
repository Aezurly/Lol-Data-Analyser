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
from utils.utils import fix_encoding

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
            analyzer = MultiGameAnalyzer("data")
            analyzer.load_all_games()
            st.session_state.multi_game_analyzer = analyzer
            st.success(f"✅ Loaded {analyzer.games_analyzed} games successfully")
    
    return st.session_state.multi_game_analyzer

def display_player_rankings(analyzer):
    """Display player rankings table"""
    st.subheader("📋 Player Table")
      # Get player stats and convert to DataFrame
    player_stats = []
    for player_name, stats_obj in analyzer.player_stats.items():
        if stats_obj.games_played > 0:              
            player_stats.append({
                'Player': fix_encoding(player_name),
                'Position': stats_obj.get_most_played_position(),
                'Most Played': stats_obj.get_most_played_champion(),
                'Games': stats_obj.games_played,
                'Win Rate': round(stats_obj.get_win_rate(), 1),
                'Avg KDA': round(stats_obj.get_average_kda(), 2),
                'CS/min': round(stats_obj.get_average_cs_per_minute(), 1),
                'Dmg/min': round(stats_obj.get_average_damage_per_minute(), 1),
                'DMG/Gold': round(stats_obj.get_average_damage_per_gold(), 2),
                'Vision/min': round(stats_obj.get_average_vision_score_per_minute(), 2),  
                'Kills/Games': round(stats_obj.total_kills / stats_obj.games_played, 2) if stats_obj.games_played > 0 else 0,
                'Deaths/Games': round(stats_obj.total_deaths / stats_obj.games_played, 2) if stats_obj.games_played > 0 else 0,
            })
    
    df = pd.DataFrame(player_stats)
    if df.empty:
        st.warning("No player data available")
        return df
    
    # Sort options
    sort_by = st.selectbox(
        "Sort by:",
        ['Win Rate', 'Avg KDA', 'Games', 'Dmg/min', 'CS/min', 'Vision/min'],
        key="player_rankings_sort"    
        )
    
    df_sorted = df.sort_values(sort_by, ascending=False)    # Display table with formatted Win Rate column
    st.dataframe(
        df_sorted, 
        use_container_width=True, 
        hide_index=True,
        column_config={
            "Win Rate": st.column_config.NumberColumn(
                "Win Rate",
                help="Win rate percentage",
                format="percent"
            )
        }
    )
    
    return df_sorted

def display_search_functionality(analyzer):
    """Display player search functionality"""
    st.subheader("🔍 Player Search")
    
    # Search input
    search_term = st.text_input("Search for a player:", placeholder="Enter player name...")
    
    if search_term:
        # Find matching players
        matching_players = []
        for player_name in analyzer.player_stats.keys():
            if search_term.lower() in player_name.lower():
                matching_players.append(player_name)
        
        if matching_players:
            st.success(f"Found {len(matching_players)} matching player(s)")
            
            # Display each matching player's detailed stats
            for player_name in matching_players:
                with st.expander(f"📊 {fix_encoding(player_name)} - Detailed Stats"):
                    display_player_detailed_stats(analyzer, player_name)
        else:
            st.warning(f"No players found matching '{search_term}'")

def display_player_detailed_stats(analyzer, player_name):
    """Display detailed stats for a specific player"""
    stats = analyzer.player_stats.get(player_name)
    if not stats:
        st.error(f"No stats found for {player_name}")
        return
    
    # Display summary metrics using PlayerStats object methods
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Games Played", stats.games_played)
    
    with col2:
        st.metric("Most Played Champion", stats.get_most_played_champion())
    
    with col3:
        st.metric("Most Played Position", stats.get_most_played_position())
    
    with col4:
        st.metric("Avg KDA", f"{stats.get_average_kda():.2f}")
    # Additional detailed metrics
    st.write("**Detailed Statistics:**")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Dmg/min", f"{stats.get_average_damage_per_minute():.1f}")
        st.metric("CS/min", f"{stats.get_average_cs_per_minute():.1f}")
    
    with col2:
        st.metric("Vision/min", f"{stats.get_average_vision_score_per_minute():.2f}")
        st.metric("DMG/Gold", f"{stats.get_average_damage_per_gold():.2f}")
    
    with col3:
        st.metric("Total Kills", stats.total_kills)
        st.metric("Total Deaths", stats.total_deaths)
    
    # Champion breakdown
    if stats.champions_played:
        st.write("**Champions Played:**")
        champions_df = pd.DataFrame([
            {'Champion': champion, 'Games': count}
            for champion, count in stats.champions_played.items()
        ]).sort_values('Games', ascending=False)
        st.dataframe(champions_df, use_container_width=True, hide_index=True)
    
    # Position breakdown
    if stats.positions_played:
        st.write("**Positions Played:**")
        positions_df = pd.DataFrame([
            {'Position': position, 'Games': count}
            for position, count in stats.positions_played.items()
        ]).sort_values('Games', ascending=False)
        st.dataframe(positions_df, use_container_width=True, hide_index=True)

def display_champion_analytics(analyzer):
    """Display champion analytics"""
    st.subheader("🎯 Champion Analytics")
    
    # Note: Champion analytics by individual games is not available with current PlayerStats structure
    st.info("📊 Champion analytics feature coming soon!")
    st.write("This feature requires individual game data which is not currently stored in the PlayerStats objects.")
    
    # Show champions played by each player instead
    st.write("**Champions Played by Players:**")
    
    all_champions = {}
    for player_name, stats in analyzer.player_stats.items():
        if stats.games_played > 0:
            most_played = stats.get_most_played_champion()
            if most_played != "Unknown":
                if most_played not in all_champions:
                    all_champions[most_played] = []
                all_champions[most_played].append(f"{fix_encoding(player_name)} ({stats.champions_played[most_played]} games)")
    
    if all_champions:
        for champion, players in sorted(all_champions.items()):
            with st.expander(f"🎭 {champion}"):
                for player in players:
                    st.write(f"• {player}")
    else:
        st.warning("No champion data available")

def main():
    """Main multi-game analysis page"""
    st.title("🌌 Global Stats")
    st.write("Analyze performance across multiple games")
    
    try:
        # Load analyzer
        analyzer = load_multi_game_analyzer()
        
        if analyzer.games_analyzed == 0:
            st.error("❌ No games were successfully analyzed")
            st.info("Please check that there are valid JSON game files in the data directory")
            return
        
        # Display summary
        st.success(f"📊 Analyzing {analyzer.games_analyzed} games")
        
        # Main sections
        tab1, tab2, tab3 = st.tabs(["📋 Player Table", "🔍 Player Search", "🎯 Champion Analytics"])
        
        with tab1:
            display_player_rankings(analyzer)
        
        with tab2:
            display_search_functionality(analyzer)
        
        with tab3:
            display_champion_analytics(analyzer)
            
    except Exception as e:
        st.error(f"❌ Error in multi-game analysis: {str(e)}")
        st.info("Please check that the data directory contains valid JSON game files.")

# Run the main function
if __name__ == "__main__":
    main()
else:
    # When imported as a page, run directly
    main()
