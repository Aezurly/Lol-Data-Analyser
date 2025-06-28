# VIEW: Single game analysis page for Streamlit interface
"""
Single game analysis page - replicates terminal single game functionality
Displays game info, participant stats, charts and visualizations
"""

import streamlit as st
import os
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd

# Import models and utilities
from models.game_data import GameData
from views.shared.game_vizualizer import GameVisualizer
from views.streamlit.components.player_card import display_participants_cards_grid
from utils.utils import fix_encoding
from constants import (
    POSITION_ICON_URLS, DEFAULT_POSITION_ICON_URL, TEAM_COLORS, 
    TEAM_1_NAME, TEAM_2_NAME, WIN_EMOJI, LOSE_EMOJI, TEAM_1_ID, TEAM_2_ID,
    TEAM_1_LABEL, TEAM_2_LABEL
)

# Configure page
st.set_page_config(
    page_title="Single Game Analysis",
    page_icon="⚔️",
    layout="wide"
)

def get_available_games():
    """Get list of available game files"""
    data_dir = "data"
    if not os.path.exists(data_dir):
        return []
    
    return [f for f in os.listdir(data_dir) if f.endswith('.json')]

def display_game_info(game_data):
    """Display basic game information"""
    if not game_data.data:
        st.error("No game data available")
        return
    
    # Game info in columns
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Match Date", game_data.get_date_string())
        
    with col2:
        st.metric("Game Duration", game_data.get_game_duration_formatted())
    
    with col3:
        st.metric("Game Version", game_data.get_version())
    
    # Team info - calculate from participants
    participants = game_data.get_all_participants()
    team1_participants = [p for p in participants if p.get_team() == TEAM_1_ID]
    team2_participants = [p for p in participants if p.get_team() == "200"]
    
    if team1_participants and team2_participants:
        col1, col2 = st.columns(2)
        
        with col1:
            team1_wins = any(p.get_win() for p in team1_participants)
            team1_result = WIN_EMOJI if team1_wins else LOSE_EMOJI
            team1_kills = sum(p.get_kills() for p in team1_participants)
            team1_deaths = sum(p.get_deaths() for p in team1_participants)
            team1_assists = sum(p.get_assists() for p in team1_participants)
            st.subheader(f"{TEAM_1_NAME} - {team1_result} - {team1_kills}/{team1_deaths}/{team1_assists}")

        with col2:
            team2_wins = any(p.get_win() for p in team2_participants)
            team2_result = WIN_EMOJI if team2_wins else LOSE_EMOJI
            team2_kills = sum(p.get_kills() for p in team2_participants)
            team2_deaths = sum(p.get_deaths() for p in team2_participants)
            team2_assists = sum(p.get_assists() for p in team2_participants)
            st.subheader(f"{TEAM_2_NAME} - {team2_result} - {team2_kills}/{team2_deaths}/{team2_assists}")

def display_participants_table(participants, game_data):
    """Display participants in a table format"""
    if not participants:
        st.warning("No participants data available")
        return

    game_duration_seconds = game_data.get_game_duration()
    game_duration_minutes = max(game_duration_seconds / 60, 1)

    # Convert participants to DataFrame
    participant_data = []
    for participant in participants:
        total_damage = participant.get_total_damage()
        damage_per_minute = round(total_damage / game_duration_minutes, 1)

        # Get position and map to icon using constants
        position = participant.get_position()
        position_icon = POSITION_ICON_URLS.get(position, DEFAULT_POSITION_ICON_URL)
        
        participant_data.append({
            'Position': position_icon,
            'Player': fix_encoding(participant.get_name()),
            'Champion': participant.get_champion(),
            'Level': participant.get_level(),
            'KDA': f"{participant.get_kills()}/{participant.get_deaths()}/{participant.get_assists()} ({participant.get_kda():.1f})",
            'CS': participant.get_cs(),
            'Gold': participant.get_gold_spent(),
            'Dmg/min': damage_per_minute,
            'Team': TEAM_1_NAME if participant.get_team() == TEAM_1_ID else TEAM_2_NAME
        })
    
    df = pd.DataFrame(participant_data)
    
    column_config = {
        "Position": st.column_config.ImageColumn(
            "Role",
            help="Player position/role",
            width=16
        ),
        "Level": st.column_config.NumberColumn(
            "Level",
            help="Player level",
            width=20
        )
    }
    
    # Display table with styling
    st.subheader("📊 Players Overview")
    
    # Determine which teams won
    team1_won = any(p.get_win() for p in participants if p.get_team() == TEAM_1_ID)
    team2_won = any(p.get_win() for p in participants if p.get_team() == TEAM_2_ID)
    
    # Team 1
    team1_df = df[df['Team'] == TEAM_1_NAME].drop('Team', axis=1)
    if not team1_df.empty:
        team1_status = f"• Win {WIN_EMOJI}" if team1_won else f"• Defeat {LOSE_EMOJI}"
        st.write(f"**{TEAM_1_NAME} {team1_status}**")
        st.dataframe(team1_df, use_container_width=True, hide_index=True, column_config=column_config)
    
    # Team 2  
    team2_df = df[df['Team'] == TEAM_2_NAME].drop('Team', axis=1)
    if not team2_df.empty:
        team2_status = f"• Win {WIN_EMOJI}" if team2_won else f"• Defeat {LOSE_EMOJI}"
        st.write(f"**{TEAM_2_NAME} {team2_status}**")
        st.dataframe(team2_df, use_container_width=True, hide_index=True, column_config=column_config)

def create_damage_chart(participants):
    """Create damage dealt chart"""
    if not participants:
        return None
    
    data = []
    for participant in participants:
        data.append({
            'Player': fix_encoding(participant.get_name()),
            'Damage': participant.get_total_damage(),
            'Team': TEAM_1_LABEL if participant.get_team() == TEAM_1_ID else TEAM_2_LABEL
        })
    
    df = pd.DataFrame(data)
    
    fig = px.bar(
        df, 
        x='Player', 
        y='Damage', 
        color='Team',
        title='Total Damage Dealt to Champions',
        color_discrete_map=TEAM_COLORS
    )
    
    fig.update_xaxes(tickangle=45)
    fig.update_layout(height=500)
    
    return fig

def create_kda_chart(participants):
    """Create KDA chart"""
    if not participants:
        return None
    
    data = []
    for participant in participants:
        kda_ratio = participant.get_kda()
        
        data.append({
            'Player': fix_encoding(participant.get_name()),
            'KDA Ratio': kda_ratio,
            'Kills': participant.get_kills(),
            'Deaths': participant.get_deaths(),
            'Assists': participant.get_assists(),
            'Team': TEAM_1_LABEL if participant.get_team() == TEAM_1_ID else TEAM_2_LABEL
        })
    
    df = pd.DataFrame(data)
    
    fig = px.bar(
        df, 
        x='Player', 
        y='KDA Ratio', 
        color='Team',
        title='KDA Ratio by Player',
        color_discrete_map=TEAM_COLORS,
        hover_data=['Kills', 'Deaths', 'Assists']
    )
    
    fig.update_xaxes(tickangle=45)
    fig.update_layout(height=500)
    
    return fig

def create_vision_chart(participants):
    """Create vision score chart"""
    if not participants:
        return None
    
    data = []
    for participant in participants:
        data.append({
            'Player': fix_encoding(participant.get_name()),
            'Vision Score': participant.get_vision_score(),
            'Team': TEAM_1_LABEL if participant.get_team() == TEAM_1_ID else TEAM_2_LABEL
        })
    
    df = pd.DataFrame(data)
    
    fig = px.bar(
        df, 
        x='Player', 
        y='Vision Score', 
        color='Team',
        title='Vision Score by Player',
        color_discrete_map=TEAM_COLORS
    )
    
    fig.update_xaxes(tickangle=45)
    fig.update_layout(height=500)
    
    return fig

def create_damage_per_gold_chart(participants):
    """Create damage per gold efficiency chart"""
    if not participants:
        return None
    
    data = []
    for participant in participants:
        efficiency = participant.get_damage_per_gold()
        
        data.append({
            'Player': fix_encoding(participant.get_name()),
            'Damage per Gold': efficiency,
            'Total Damage': participant.get_total_damage(),
            'Gold Spent': participant.get_gold_spent(),
            'Team': TEAM_1_LABEL if participant.get_team() == TEAM_1_ID else TEAM_2_LABEL
        })
    
    df = pd.DataFrame(data)
    
    fig = px.bar(
        df, 
        x='Player', 
        y='Damage per Gold', 
        color='Team',
        title='Damage per Gold Efficiency',
        color_discrete_map=TEAM_COLORS,
        hover_data=['Total Damage', 'Gold Spent']
    )
    
    fig.update_xaxes(tickangle=45)
    fig.update_layout(height=500)
    
    return fig

def create_cs_chart(participants):
    """Create CS (Creep Score) chart"""
    if not participants:
        return None
    
    data = []
    for participant in participants:
        data.append({
            'Player': fix_encoding(participant.get_name()),
            'CS': participant.get_cs(),
            'Team': TEAM_1_LABEL if participant.get_team() == TEAM_1_ID else TEAM_2_LABEL
        })
    
    df = pd.DataFrame(data)
    
    fig = px.bar(
        df, 
        x='Player', 
        y='CS', 
        color='Team',
        title='Creep Score (CS) by Player',
        color_discrete_map=TEAM_COLORS
    )
    
    fig.update_xaxes(tickangle=45)
    fig.update_layout(height=500)
    
    return fig

def display_participants_cards(participants):
    """Display participant cards in a grid"""
    if not participants:
        st.warning("No participants data available")
        return
    
    st.subheader("🃏 Profiles")
    
    # Display participants using the component
    display_participants_cards_grid(participants, cols_per_row=5, show_profile_buttons=True)

def main():
    """Main single game analysis page"""
    st.title("📊 Single Game Analysis")
    st.write("Analyze individual game performance and statistics")
    
    # Check if a game was selected from home page
    selected_game_path = st.session_state.get('selected_game', None)
    
    # Game file selection
    available_games = get_available_games()
    
    if not available_games:
        st.error("❌ No game files found in the data directory")
        return
    
    # If a game was selected from home page, find its filename
    if selected_game_path:
        selected_filename = os.path.basename(selected_game_path)
        if selected_filename in available_games:
            default_index = available_games.index(selected_filename)
        else:
            default_index = 0
            st.warning(f"Selected game {selected_filename} not found, using first available game")
    else:
        default_index = 0
    
    selected_game = st.selectbox(
        "Select a game to analyze:",
        available_games,
        index=default_index,
        help="Choose a JSON game file from the data directory"
    )
    
    # Clear the selected game from session state after using it
    if 'selected_game' in st.session_state:
        del st.session_state.selected_game
    
    if not selected_game:
        st.warning("Please select a game file to continue")
        return
    
    # Load game data
    try:
        file_path = os.path.join("data", selected_game)
        game_data = GameData(file_path)
        
        if not game_data.data:
            st.error(f"❌ Could not load game data from {selected_game}")
            return
        
        participants = game_data.get_all_participants()
        
        # Game information section
        st.header("🎮 Game Overview")
        display_game_info(game_data)
          # Participants table
        st.header("👥 Players")
        display_participants_cards(participants)
        display_participants_table(participants, game_data)
        
        # Charts section
        st.header("📈 Performance Charts")
        
        # Display charts in 2 columns
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("💥 Total Damage Dealt")
            fig_damage = create_damage_chart(participants)
            if fig_damage:
                st.plotly_chart(fig_damage, use_container_width=True)
        
        with col2:
            st.subheader("🌾 Creep Score (CS)")
            fig_cs = create_cs_chart(participants)
            if fig_cs:
                st.plotly_chart(fig_cs, use_container_width=True)
        
        # Second row of charts
        col3, col4 = st.columns(2)
        
        with col3:
            st.subheader("💰 Damage per Gold Efficiency")
            fig_efficiency = create_damage_per_gold_chart(participants)
            if fig_efficiency:
                st.plotly_chart(fig_efficiency, use_container_width=True)
        
        with col4:
            st.subheader("👁️ Vision Score")
            fig_vision = create_vision_chart(participants)
            if fig_vision:
                st.plotly_chart(fig_vision, use_container_width=True)
        
        # Raw data section (collapsible)
        with st.expander("🔍 Raw Game Data"):
            st.json(game_data.data, expanded=False)
            
    except Exception as e:
        st.error(f"❌ Error loading game data: {str(e)}")
        st.info("Please check that the selected file exists and is a valid JSON game file.")

# Run the main function
if __name__ == "__main__":
    main()
else:
    # When imported as a page, run directly
    main()
