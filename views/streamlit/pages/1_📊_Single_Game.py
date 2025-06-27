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
from utils.utils import fix_encoding

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
    team1_participants = [p for p in participants if p.get_team() == "100"]
    team2_participants = [p for p in participants if p.get_team() == "200"]
    
    if team1_participants and team2_participants:
        col1, col2 = st.columns(2)
        
        with col1:
            team1_wins = any(p.get_win() for p in team1_participants)
            team1_result = "Victory" if team1_wins else "Defeat"
            team1_kills = sum(p.get_kills() for p in team1_participants)
            st.subheader(f"🔵 Team 1 - {team1_result}")
            st.write(f"**Total Kills:** {team1_kills}")
            player_names = [fix_encoding(p.get_name()) for p in team1_participants]
            st.write(f"**Players:** {', '.join(player_names)}")
        
        with col2:
            team2_wins = any(p.get_win() for p in team2_participants)
            team2_result = "Victory" if team2_wins else "Defeat"
            team2_kills = sum(p.get_kills() for p in team2_participants)
            st.subheader(f"🔴 Team 2 - {team2_result}")
            st.write(f"**Total Kills:** {team2_kills}")
            player_names = [fix_encoding(p.get_name()) for p in team2_participants]
            st.write(f"**Players:** {', '.join(player_names)}")

def display_participants_table(participants, game_data):
    """Display participants in a table format"""
    if not participants:
        st.warning("No participants data available")
        return
    
    # Get game duration in minutes using the model method
    game_duration_seconds = game_data.get_game_duration()
    game_duration_minutes = max(game_duration_seconds / 60, 1)  # Avoid division by zero
    
    # Convert participants to DataFrame
    participant_data = []
    for participant in participants:
        total_damage = participant.get_total_damage()
        damage_per_minute = round(total_damage / game_duration_minutes, 1)
        
        participant_data.append({
            'Player': fix_encoding(participant.get_name()),
            'Champion': participant.get_champion(),
            'Position': participant.get_position(),
            'Level': participant.get_level(),
            '(K+A)/D': participant.get_kda(),
            'KDA': f"{participant.get_kills()}/{participant.get_deaths()}/{participant.get_assists()}",
            'CS': participant.get_cs(),
            'Gold': participant.get_gold_spent(),
            'Dmg/min': damage_per_minute,
            'Team': "🔵 Team 1" if participant.get_team() == "100" else "🔴 Team 2"
        })
    
    df = pd.DataFrame(participant_data)
    
    # Display table with styling
    st.subheader("📊 Players Overview")
    
    # Team 1
    # Determine which teams won
    team1_won = any(p.get_win() for p in participants if p.get_team() == "100")
    team2_won = any(p.get_win() for p in participants if p.get_team() == "200")
    
    # Team 1
    team1_df = df[df['Team'] == "🔵 Team 1"].drop('Team', axis=1)
    if not team1_df.empty:
        team1_status = "• Win 🏆" if team1_won else "• Defeat 💀"
        st.write(f"**🔵 Team 1 {team1_status}**")
        st.dataframe(team1_df, use_container_width=True, hide_index=True)
    
    # Team 2  
    team2_df = df[df['Team'] == "🔴 Team 2"].drop('Team', axis=1)
    if not team2_df.empty:
        team2_status = "• Win 🏆" if team2_won else "• Defeat 💀"
        st.write(f"**🔴 Team 2 {team2_status}**")
        st.dataframe(team2_df, use_container_width=True, hide_index=True)

def create_damage_chart(participants):
    """Create damage dealt chart"""
    if not participants:
        return None
    
    data = []
    for participant in participants:
        data.append({
            'Player': fix_encoding(participant.get_name()),
            'Damage': participant.get_total_damage(),
            'Team': "Team 1" if participant.get_team() == "100" else "Team 2"
        })
    
    df = pd.DataFrame(data)
    
    fig = px.bar(
        df, 
        x='Player', 
        y='Damage', 
        color='Team',
        title='Total Damage Dealt to Champions',
        color_discrete_map={'Team 1': '#3498db', 'Team 2': '#e74c3c'}
    )
    
    fig.update_xaxis(tickangle=45)
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
            'Team': "Team 1" if participant.get_team() == "100" else "Team 2"
        })
    
    df = pd.DataFrame(data)
    
    fig = px.bar(
        df, 
        x='Player', 
        y='KDA Ratio', 
        color='Team',
        title='KDA Ratio by Player',
        color_discrete_map={'Team 1': '#3498db', 'Team 2': '#e74c3c'},
        hover_data=['Kills', 'Deaths', 'Assists']
    )
    
    fig.update_xaxis(tickangle=45)
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
            'Team': "Team 1" if participant.get_team() == "100" else "Team 2"
        })
    
    df = pd.DataFrame(data)
    
    fig = px.bar(
        df, 
        x='Player', 
        y='Vision Score', 
        color='Team',
        title='Vision Score by Player',
        color_discrete_map={'Team 1': '#3498db', 'Team 2': '#e74c3c'}
    )
    
    fig.update_xaxis(tickangle=45)
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
            'Team': "Team 1" if participant.get_team() == "100" else "Team 2"
        })
    
    df = pd.DataFrame(data)
    
    fig = px.bar(
        df, 
        x='Player', 
        y='Damage per Gold', 
        color='Team',
        title='Damage per Gold Efficiency',
        color_discrete_map={'Team 1': '#3498db', 'Team 2': '#e74c3c'},
        hover_data=['Total Damage', 'Gold Spent']
    )
    
    fig.update_xaxis(tickangle=45)
    fig.update_layout(height=500)
    
    return fig

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
        st.header("🎮 Game Information")
        display_game_info(game_data)
          # Participants table
        st.header("👥 Participants")
        display_participants_table(participants, game_data)
          # Team damage overview
        st.header("⚔️ Team Damage Summary")
        team1_damage = sum(p.get_total_damage() for p in participants if p.get_team() == "100")
        team2_damage = sum(p.get_total_damage() for p in participants if p.get_team() == "200")
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("🔵 Team 1 Total Damage", f"{team1_damage:,}")
        with col2:
            st.metric("🔴 Team 2 Total Damage", f"{team2_damage:,}")
        
        # Charts section
        st.header("📈 Performance Charts")
        
        # Chart selection
        chart_option = st.selectbox(
            "Select a chart to display:",
            [
                "Total Damage Dealt",
                "KDA Ratio", 
                "Damage per Gold Efficiency",
                "Vision Score"
            ]
        )
        
        # Display selected chart
        if chart_option == "Total Damage Dealt":
            fig = create_damage_chart(participants)
            if fig:
                st.plotly_chart(fig, use_container_width=True)
        
        elif chart_option == "KDA Ratio":
            fig = create_kda_chart(participants)
            if fig:
                st.plotly_chart(fig, use_container_width=True)
        
        elif chart_option == "Damage per Gold Efficiency":
            fig = create_damage_per_gold_chart(participants)
            if fig:
                st.plotly_chart(fig, use_container_width=True)
        
        elif chart_option == "Vision Score":
            fig = create_vision_chart(participants)
            if fig:
                st.plotly_chart(fig, use_container_width=True)
        
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
