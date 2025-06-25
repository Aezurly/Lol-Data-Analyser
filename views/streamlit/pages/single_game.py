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
    
    info = game_data.data['info']
    
    # Game info in columns
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Game Duration", f"{info.get('gameDuration', 0) // 60}:{info.get('gameDuration', 0) % 60:02d}")
    
    with col2:
        st.metric("Game Mode", info.get('gameMode', 'Unknown'))
    
    with col3:
        st.metric("Game Version", info.get('gameVersion', 'Unknown'))
    
    # Team info
    teams = info.get('teams', [])
    if len(teams) >= 2:
        col1, col2 = st.columns(2)
        
        with col1:
            team1 = teams[0]
            team1_win = "Victory" if team1.get('win', False) else "Defeat"
            st.subheader(f"🔵 Team 1 - {team1_win}")
            st.write(f"**Kills:** {team1.get('objectives', {}).get('champion', {}).get('kills', 0)}")
            st.write(f"**Dragons:** {team1.get('objectives', {}).get('dragon', {}).get('kills', 0)}")
            st.write(f"**Barons:** {team1.get('objectives', {}).get('baron', {}).get('kills', 0)}")
        
        with col2:
            team2 = teams[1]
            team2_win = "Victory" if team2.get('win', False) else "Defeat"
            st.subheader(f"🔴 Team 2 - {team2_win}")
            st.write(f"**Kills:** {team2.get('objectives', {}).get('champion', {}).get('kills', 0)}")
            st.write(f"**Dragons:** {team2.get('objectives', {}).get('dragon', {}).get('kills', 0)}")
            st.write(f"**Barons:** {team2.get('objectives', {}).get('baron', {}).get('kills', 0)}")

def display_participants_table(participants):
    """Display participants in a table format"""
    if not participants:
        st.warning("No participants data available")
        return
    
    # Convert participants to DataFrame
    participant_data = []
    for participant in participants:
        participant_data.append({
            'Player': fix_encoding(participant.get('summonerName', 'Unknown')),
            'Champion': participant.get('championName', 'Unknown'),
            'Position': participant.get('teamPosition', 'Unknown'),
            'Level': participant.get('champLevel', 0),
            'Kills': participant.get('kills', 0),
            'Deaths': participant.get('deaths', 0),
            'Assists': participant.get('assists', 0),
            'KDA': f"{participant.get('kills', 0)}/{participant.get('deaths', 0)}/{participant.get('assists', 0)}",
            'CS': participant.get('totalMinionsKilled', 0) + participant.get('neutralMinionsKilled', 0),
            'Gold': participant.get('goldEarned', 0),
            'Damage': participant.get('totalDamageDealtToChampions', 0),
            'Team': "🔵 Team 1" if participant.get('teamId') == 100 else "🔴 Team 2"
        })
    
    df = pd.DataFrame(participant_data)
    
    # Display table with styling
    st.subheader("📊 Participants Overview")
    
    # Team 1
    team1_df = df[df['Team'] == "🔵 Team 1"].drop('Team', axis=1)
    if not team1_df.empty:
        st.write("**🔵 Team 1**")
        st.dataframe(team1_df, use_container_width=True, hide_index=True)
    
    # Team 2  
    team2_df = df[df['Team'] == "🔴 Team 2"].drop('Team', axis=1)
    if not team2_df.empty:
        st.write("**🔴 Team 2**")
        st.dataframe(team2_df, use_container_width=True, hide_index=True)

def create_damage_chart(participants):
    """Create damage dealt chart"""
    if not participants:
        return None
    
    data = []
    for participant in participants:
        data.append({
            'Player': fix_encoding(participant.get('summonerName', 'Unknown')),
            'Damage': participant.get('totalDamageDealtToChampions', 0),
            'Team': "Team 1" if participant.get('teamId') == 100 else "Team 2"
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
        kills = participant.get('kills', 0)
        deaths = max(participant.get('deaths', 0), 1)  # Avoid division by zero
        assists = participant.get('assists', 0)
        kda_ratio = (kills + assists) / deaths
        
        data.append({
            'Player': fix_encoding(participant.get('summonerName', 'Unknown')),
            'KDA Ratio': kda_ratio,
            'Kills': kills,
            'Deaths': deaths,
            'Assists': assists,
            'Team': "Team 1" if participant.get('teamId') == 100 else "Team 2"
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
            'Player': fix_encoding(participant.get('summonerName', 'Unknown')),
            'Vision Score': participant.get('visionScore', 0),
            'Team': "Team 1" if participant.get('teamId') == 100 else "Team 2"
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
        gold = max(participant.get('goldEarned', 1), 1)  # Avoid division by zero
        damage = participant.get('totalDamageDealtToChampions', 0)
        efficiency = damage / gold
        
        data.append({
            'Player': fix_encoding(participant.get('summonerName', 'Unknown')),
            'Damage per Gold': efficiency,
            'Total Damage': damage,
            'Gold Earned': gold,
            'Team': "Team 1" if participant.get('teamId') == 100 else "Team 2"
        })
    
    df = pd.DataFrame(data)
    
    fig = px.bar(
        df, 
        x='Player', 
        y='Damage per Gold', 
        color='Team',
        title='Damage per Gold Efficiency',
        color_discrete_map={'Team 1': '#3498db', 'Team 2': '#e74c3c'},
        hover_data=['Total Damage', 'Gold Earned']
    )
    
    fig.update_xaxis(tickangle=45)
    fig.update_layout(height=500)
    
    return fig

def single_game_page():
    """Main single game analysis page"""
    st.title("📊 Single Game Analysis")
    st.write("Analyze individual game performance and statistics")
    
    # Game file selection
    available_games = get_available_games()
    
    if not available_games:
        st.error("❌ No game files found in the data directory")
        return
    
    selected_game = st.selectbox(
        "Select a game to analyze:",
        available_games,
        help="Choose a JSON game file from the data directory"
    )
    
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
        display_participants_table(participants)
        
        # Team damage overview
        st.header("⚔️ Team Damage Summary")
        team1_damage = sum(p.get('totalDamageDealtToChampions', 0) for p in participants if p.get('teamId') == 100)
        team2_damage = sum(p.get('totalDamageDealtToChampions', 0) for p in participants if p.get('teamId') == 200)
        
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
