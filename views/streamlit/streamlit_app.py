# VIEW: Main Streamlit application entry point
"""
Streamlit web interface for LoL Data Analyzer
Complete replication of terminal functionality in web interface
"""

import streamlit as st
import os
import sys
from config import STREAMLIT_CONFIG, APP_VERSION, APP_DESCRIPTION, DATA_DIRECTORY

# Add the project root to Python path for imports
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if project_root not in sys.path:
    sys.path.append(project_root)

# Import page modules with try/except for better error handling
try:
    from views.streamlit.pages.single_game import single_game_page
    from views.streamlit.pages.multi_game import multi_game_page  
    from views.streamlit.pages.team_analysis import team_analysis_page
except ImportError as e:
    st.error(f"Error importing page modules: {e}")
    st.stop()

# Configure Streamlit page
st.set_page_config(**STREAMLIT_CONFIG)

def show_welcome_page():
    """Show the welcome/home page"""
    
    # Header
    st.title("🎮 LoL Data Analyzer")
    st.subheader(f"Version {APP_VERSION}")
    st.write(APP_DESCRIPTION)
    
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
    
    # Quick navigation
    st.header("🚀 Quick Start")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📊 Single Game Analysis", use_container_width=True):
            st.session_state.page = "single_game"
            st.rerun()
    
    with col2:
        if st.button("📈 Multi Game Analysis", use_container_width=True):
            st.session_state.page = "multi_game"
            st.rerun()
    
    with col3:
        if st.button("🏆 Team Analysis", use_container_width=True):
            st.session_state.page = "team_analysis"
            st.rerun()

def show_sidebar_navigation():
    """Show the sidebar navigation"""
    st.sidebar.title("🎯 Navigation")
    
    # Navigation menu
    page = st.sidebar.selectbox(
        "Choose a section:",
        ["🏠 Home", "📊 Single Game", "📈 Multi Game", "🏆 Team Analysis"],
        key="navigation"
    )
    
    # Map display names to page keys
    page_mapping = {
        "🏠 Home": "home",
        "📊 Single Game": "single_game", 
        "📈 Multi Game": "multi_game",
        "🏆 Team Analysis": "team_analysis"
    }
    
    selected_page = page_mapping[page]
    
    # Update session state if page changed
    if "page" not in st.session_state or st.session_state.page != selected_page:
        st.session_state.page = selected_page
        st.rerun()
    
    # Show current data status in sidebar
    st.sidebar.markdown("---")
    st.sidebar.subheader("📁 Data Status")
    
    if os.path.exists(DATA_DIRECTORY):
        json_files = [f for f in os.listdir(DATA_DIRECTORY) if f.endswith('.json')]
        st.sidebar.success(f"✅ {len(json_files)} games available")
    else:
        st.sidebar.error("❌ No data directory")

def main():
    """Main Streamlit application"""
    
    # Initialize session state
    if "page" not in st.session_state:
        st.session_state.page = "home"
    
    # Show sidebar navigation
    show_sidebar_navigation()
    
    # Route to appropriate page
    if st.session_state.page == "home":
        show_welcome_page()
    elif st.session_state.page == "single_game":
        single_game_page()
    elif st.session_state.page == "multi_game":
        multi_game_page()
    elif st.session_state.page == "team_analysis":
        team_analysis_page()
    else:
        show_welcome_page()  # Fallback to home
    
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
    
    # Interactive test
    st.header("🎛️ Interactive Test")
    
    name = st.text_input("Enter your summoner name:", placeholder="e.g. Aezurly")
    
    if name:
        st.success(f"Hello {name}! The Streamlit interface is working correctly! 🎉")
    
    # Future features preview
    st.header("🚀 Coming Soon")
    
    st.info("""
    **Planned Features:**
    - 📈 Interactive game analysis
    - 📊 Multi-game statistics dashboard  
    - 👥 Team performance comparison
    - 📱 Responsive design
    - 🎨 Advanced visualizations with Plotly
    """)
    
    # Footer
    st.markdown("---")
    st.caption("🔧 Streamlit Test Page - LoL Data Analyzer")

if __name__ == "__main__":
    main()
