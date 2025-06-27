# VIEW: Main Streamlit application entry point
"""
Streamlit web interface for LoL Data Analyzer
Main Streamlit application - Home page
"""

import streamlit as st
import os
import sys
from config import STREAMLIT_CONFIG, APP_VERSION, APP_DESCRIPTION, DATA_DIRECTORY

# Add the project root to Python path for imports
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if project_root not in sys.path:
    sys.path.append(project_root)

# Import model for player search
from models.multi_game_analyzer import MultiGameAnalyzer
from utils.utils import fix_encoding

# Configure Streamlit page
st.set_page_config(**STREAMLIT_CONFIG)

def load_multi_game_analyzer():
    """Load and cache the multi-game analyzer"""
    if 'multi_game_analyzer' not in st.session_state:
        with st.spinner("Loading and analyzing all games..."):
            analyzer = MultiGameAnalyzer("data")
            analyzer.load_all_games()
            st.session_state.multi_game_analyzer = analyzer
    
    return st.session_state.multi_game_analyzer

def display_player_search():
    """Display player search functionality on home page"""
    st.subheader("🔍 Player Search")
    
    # Search input
    search_term = st.text_input("Search for a player:", placeholder="Enter player name...")
    
    if search_term:
        try:
            # Load analyzer
            analyzer = load_multi_game_analyzer()
            
            # Search for players
            matching_players = analyzer.search_players(search_term)
            
            if matching_players:
                st.caption(f"Found {len(matching_players)} matching player(s)")
                # Create cards in columns (3 per row)
                cols_per_row = 3
                for i in range(0, len(matching_players), cols_per_row):
                    cols = st.columns(cols_per_row)
                    
                    for j, player_name in enumerate(matching_players[i:i+cols_per_row]):
                        with cols[j]:
                            # Get basic player info
                            player_stats = analyzer.player_stats.get(player_name)
                            if player_stats:
                                with st.container(border=True):
                                    st.markdown(f"**{fix_encoding(player_name)}** • {player_stats.get_most_played_position()}")
                                    st.caption(f"{player_stats.games_played} games •  {player_stats.get_win_rate()*100:.1f}%")
                                    
                                    if st.button("View Profile", key=f"profile_{player_name}", use_container_width=True):
                                        st.session_state.selected_player = player_name
                                        st.switch_page("pages/4_👤_Player_Profile.py")
            else:
                st.warning(f"No players found matching '{search_term}'")
                
        except Exception as e:
            st.error(f"Error searching players: {str(e)}")

def main():
    """Main Streamlit application - Home page"""
    
    # Header
    st.title("⚔️ LoL Data Analyzer")
    st.write(f"{APP_DESCRIPTION} \t • \t Version **{APP_VERSION}**")

    # Divider
    st.markdown("---")
    
    # Player search section
    display_player_search()
    
    # Main content
    st.header("📊 Application Status")
    
    # Test data directory
    if os.path.exists(DATA_DIRECTORY):
        json_files = [f for f in os.listdir(DATA_DIRECTORY) if f.endswith('.json')]
        st.success(f"✅ Data directory found: {len(json_files)} JSON files detected")
        
        if json_files:
            st.write("**Available game files:**")
            for file in json_files[:5]:  # Show first 5 files
                st.write(f"- {file}")
            if len(json_files) > 5:
                st.write(f"... and {len(json_files) - 5} more files")
    else:
        st.error(f"❌ Data directory not found: {DATA_DIRECTORY}")
    
    # Navigation guide
    st.header("🧭 Infos")
    st.info("""
    Use the sidebar navigation to access different sections:
    - **📊 Single Game Analysis**: Analyze individual game data
    - **🌌 Global Stats**: Compare multiple games and player rankings
    - **🦦 Marmotte Flip**: Team performance analysis
    - **👤 Player Profile**: Detailed player statistics (accessible via search)
    """)
    
    # Application metrics
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            label="Interface Mode", 
            value="Streamlit",
            delta="Web Interface"
        )
    
    with col2:
        st.metric(
            label="Python Environment", 
            value="Active",
            delta="Ready"
        )
    
    with col3:
        st.metric(
            label="Streamlit Version", 
            value=st.__version__,
            delta="Installed"
        )
    
    # Footer
    st.markdown("---")
    st.caption("🔧 Home Page - LoL Data Analyzer")

if __name__ == "__main__":
    main()
