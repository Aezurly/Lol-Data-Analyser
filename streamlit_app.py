# Main entry point for Streamlit Community Cloud deployment
"""
This is the main entry point that Streamlit Community Cloud will use.
It imports and runs the actual Streamlit application.
"""

import os
import sys
import streamlit as st

# Add the project root to Python path for imports
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.append(project_root)

# Import the main application components
from config import STREAMLIT_CONFIG, APP_VERSION, APP_DESCRIPTION
from models.multi_game_analyzer import MultiGameAnalyzer
from utils.utils import fix_encoding, normalize_player_name
from constants import DATA_DIR
from views.streamlit.components import display_player_search_results, display_game_cards_grid

# Configure Streamlit page
st.set_page_config(**STREAMLIT_CONFIG)

def load_multi_game_analyzer():
    """Load and cache the multi-game analyzer"""
    if 'multi_game_analyzer' not in st.session_state:
        with st.spinner("Loading and analyzing all games..."):
            analyzer = MultiGameAnalyzer(DATA_DIR)
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
            
            display_player_search_results(search_term, analyzer)
                
        except Exception as e:
            st.error(f"Error searching players: {str(e)}")

def display_games():
    """Display recent games section on home page"""
    st.subheader("📅 Recent Games")
    
    try:
        # Load analyzer
        analyzer = load_multi_game_analyzer()
        
        # Get all games data
        games_data = analyzer.get_all_games_data()
        
        if not games_data:
            st.warning("No games found in the data directory")
            return
        
        st.caption(f"Found {len(games_data)} game(s)")

        display_game_cards_grid(games_data, analyzer, cols_per_row=2)
                        
    except Exception as e:
        st.error(f"Error loading games: {str(e)}")

def main():
    """Main Streamlit application - Home page"""
    
    # Header
    st.title("⚔️ LoL Data Analyzer")
    st.write(f"{APP_DESCRIPTION} \t • \t Version **{APP_VERSION}**")

    # Divider
    st.markdown("---")
    
    # Player search section
    display_player_search()
    
    # Divider
    st.markdown("---")
    
    # Recent games section
    display_games()
    
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
