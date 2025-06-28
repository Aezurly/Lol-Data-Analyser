"""
Shared navigation component for Streamlit pages
"""
import streamlit as st

def create_navigation(current_page="Home"):
    col1, col2, col3, col4, col5 = st.columns([1, 2, 2, 2, 2])
    
    with col1:
        st.markdown("<h4 style='text-align: center;'>⚔️</h4>", unsafe_allow_html=True)
    with col2:
        button_type = "primary" if current_page == "Home" else "secondary"
        if st.button("🏠 Home", use_container_width=True, type=button_type):
            st.switch_page("streamlit_app.py")
    
    with col3:
        button_type = "primary" if current_page == "Single Game" else "secondary"
        if st.button("📊 Single Game", use_container_width=True, type=button_type):
            st.switch_page("pages/1_📊_Single_Game.py")
    
    with col4:
        button_type = "primary" if current_page == "Global Stats" else "secondary"
        if st.button("🌌 Global Stats", use_container_width=True, type=button_type):
            st.switch_page("pages/2_🌌_Global_Stats.py")
    
    with col5:
        button_type = "primary" if current_page == "Marmotte Flip" else "secondary"
        if st.button("🦦 Marmotte Flip", use_container_width=True, type=button_type):
            st.switch_page("pages/3_🦦_Marmotte_Flip.py")
    
    
    
    st.markdown("---")
