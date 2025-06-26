# VIEW: Main Streamlit application entry point
"""
Streamlit web interface for LoL Data Analyzer
Home page using Streamlit's native page navigation
"""

import streamlit as st
import os
import sys
from config import STREAMLIT_CONFIG, APP_VERSION, APP_DESCRIPTION, DATA_DIRECTORY

# Add the project root to Python path for imports
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if project_root not in sys.path:
    sys.path.append(project_root)

# Configure Streamlit page
st.set_page_config(**STREAMLIT_CONFIG)

def main():
    """Main Streamlit application - Home page"""
    
    # Header
    st.title("� LoL Data Analyzer")
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
    
    # Navigation guide
    st.header("🧭 Navigation")
    st.info("""
    Use the sidebar navigation to access different sections:
    - **📊 Single Game Analysis**: Analyze individual game data
    - **🌌 Global Stats**: Compare multiple games
    - **🦦 Marmotte Flip**: Team performance analysis
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
    
    # Interactive test
    st.header("🎛️ Interactive Test")
    
    name = st.text_input("Enter your summoner name:", placeholder="e.g. Aezurly")
    
    if name:
        st.success(f"Hello {name}! The Streamlit interface is working correctly! 🎉")
    
    # Footer
    st.markdown("---")
    st.caption("🔧 Home Page - LoL Data Analyzer")

if __name__ == "__main__":
    main()
