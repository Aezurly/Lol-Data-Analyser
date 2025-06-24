# VIEW: Team comparison visualizations and chart generation
import matplotlib.pyplot as plt
import numpy as np
from typing import Dict, List
from models.team_analyzer import TeamAnalyzer
from models.position_comparison import PositionComparison
from utils.utils import fix_encoding

class TeamVisualizer:
    """Class for creating team comparison visualizations"""
    
    def __init__(self, team_analyzer: TeamAnalyzer):
        self.team_analyzer = team_analyzer
        self.position_comparison = PositionComparison(team_analyzer, None)
    
    def plot_position_comparison_radar(self, player_name: str, position: str):
        """Creates a radar chart comparing a player to opponents"""
        comparison = self.position_comparison.compare_player_to_opponents(player_name, position)
        
        if not comparison:
            print(f"No data available for {player_name} in position {position}")
            return
        
        # Statistics to display on the radar
        stats_to_plot = [
            ('damage', 'Damage'),
            ('kda', 'KDA'),
            ('cs_per_minute', 'CS/min'),
            ('vision_per_minute', 'Vision/min'),
            ('damage_per_gold', 'Damage/Gold')
        ]
        
        # Prepare data
        categories = [stat_display for _, stat_display in stats_to_plot]
        player_values = []
        opponent_values = []
        
        for stat_key, _ in stats_to_plot:
            player_val = comparison['player_stats'][stat_key]
            opponent_val = comparison['opponents_stats'][stat_key]
            
            # Normalize values (percentage of maximum)
            max_val = max(player_val, opponent_val)
            if max_val > 0:
                player_values.append((player_val / max_val) * 100)
                opponent_values.append((opponent_val / max_val) * 100)
            else:
                player_values.append(0)
                opponent_values.append(0)
        
        # Create radar chart
        angles = np.linspace(0, 2 * np.pi, len(categories), endpoint=False).tolist()
        
        # Close the polygon
        player_values += player_values[:1]
        opponent_values += opponent_values[:1]
        angles += angles[:1]
        
        fig, ax = plt.subplots(figsize=(10, 10), subplot_kw=dict(projection='polar'))
          # Plot lines
        ax.plot(angles, player_values, 'o-', linewidth=2, label=fix_encoding(player_name), color='blue')
        ax.fill(angles, player_values, alpha=0.25, color='blue')
        
        ax.plot(angles, opponent_values, 'o-', linewidth=2, label='Opponents (average)', color='red')
        ax.fill(angles, opponent_values, alpha=0.25, color='red')
        
        # Customize chart
        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(categories)
        ax.set_ylim(0, 100)
        ax.set_yticks([20, 40, 60, 80, 100])
        ax.set_yticklabels(['20%', '40%', '60%', '80%', '100%'])
        ax.grid(True)
        
        plt.legend(loc='upper right', bbox_to_anchor=(1.1, 1.1))
        plt.title(f'Comparison: {fix_encoding(player_name)} ({position}) vs Opponents', 
                 size=16, fontweight='bold', pad=20)
        
        plt.tight_layout()
        plt.show()
    
    def plot_team_performance_overview(self):
        """Creates a bar chart comparing all our players to opponents"""
        best_performers = self.position_comparison.get_best_performers_by_position()
        
        positions = []
        players = []
        damage_diffs = []
        kda_diffs = []
        for position, performers in best_performers.items():
            if performers:
                best_player, damage_diff = performers[0]
                positions.append(position)
                players.append(fix_encoding(best_player))
                damage_diffs.append(damage_diff)
                
                # Get KDA difference for this player
                comparison = self.position_comparison.compare_player_to_opponents(best_player, position)
                if comparison and 'kda' in comparison['differences']:
                    kda_diffs.append(comparison['differences']['kda']['percentage_diff'])
                else:
                    kda_diffs.append(0)
        
        if not positions:
            print("No data to display")
            return
        
        # Create chart
        x = np.arange(len(positions))
        width = 0.35
        
        fig, ax = plt.subplots(figsize=(12, 8))
        
        # Bars for damage
        bars1 = ax.bar(x - width/2, damage_diffs, width, label='Damage Difference (%)', 
                      color=['green' if d > 0 else 'red' for d in damage_diffs], alpha=0.7)
        
        # Bars for KDA
        bars2 = ax.bar(x + width/2, kda_diffs, width, label='KDA Difference (%)', 
                      color=['lightgreen' if d > 0 else 'lightcoral' for d in kda_diffs], alpha=0.7)
        
        # Customize chart
        ax.set_xlabel('Position')
        ax.set_ylabel('Difference in % vs Opponents')
        ax.set_title('Performance of our best players by position vs Opponents')
        ax.set_xticks(x)
        ax.set_xticklabels([f"{pos}\n({player})" for pos, player in zip(positions, players)])
        ax.legend()
        ax.grid(True, alpha=0.3)
        ax.axhline(y=0, color='black', linestyle='-', alpha=0.5)
        
        # Add values on bars
        for bar in bars1:
            height = bar.get_height()
            ax.annotate(f'{height:.1f}%',
                       xy=(bar.get_x() + bar.get_width() / 2, height),
                       xytext=(0, 3 if height >= 0 else -15),
                       textcoords="offset points",
                       ha='center', va='bottom' if height >= 0 else 'top')
        
        for bar in bars2:
            height = bar.get_height()
            ax.annotate(f'{height:.1f}%',
                       xy=(bar.get_x() + bar.get_width() / 2, height),
                       xytext=(0, 3 if height >= 0 else -15),
                       textcoords="offset points",
                       ha='center', va='bottom' if height >= 0 else 'top')
        
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        plt.show()
    
    def plot_all_players_at_position(self, position: str):
        """Compare all our players at a given position"""
        our_players = self.team_analyzer.get_our_players_by_position(position)
        
        if not our_players:
            print(f"No players found in position {position}")
            return
        
        player_names = []
        damage_diffs = []
        kda_diffs = []
        for player in our_players:
            comparison = self.position_comparison.compare_player_to_opponents(player, position)
            if comparison:
                player_names.append(fix_encoding(player))
                
                if 'damage' in comparison['differences']:
                    damage_diffs.append(comparison['differences']['damage']['percentage_diff'])
                else:
                    damage_diffs.append(0)
                
                if 'kda' in comparison['differences']:
                    kda_diffs.append(comparison['differences']['kda']['percentage_diff'])
                else:
                    kda_diffs.append(0)
        
        if not player_names:
            print(f"No comparison data for position {position}")
            return
        
        # Create chart
        x = np.arange(len(player_names))
        width = 0.35
        
        fig, ax = plt.subplots(figsize=(10, 6))
        
        bars1 = ax.bar(x - width/2, damage_diffs, width, label='Damage Difference (%)', 
                      color=['green' if d > 0 else 'red' for d in damage_diffs], alpha=0.7)
        
        bars2 = ax.bar(x + width/2, kda_diffs, width, label='KDA Difference (%)', 
                      color=['lightgreen' if d > 0 else 'lightcoral' for d in kda_diffs], alpha=0.7)
        
        ax.set_xlabel('Players')
        ax.set_ylabel('Difference in % vs Opponents')
        ax.set_title(f'All our {position} players vs Opponents')
        ax.set_xticks(x)
        ax.set_xticklabels(player_names, rotation=45, ha='right')
        ax.legend()
        ax.grid(True, alpha=0.3)
        ax.axhline(y=0, color='black', linestyle='-', alpha=0.5)
        
        plt.tight_layout()
        plt.show()
    
    def plot_detailed_comparison(self, player_name: str, position: str):
        """Detailed chart with all statistics"""
        comparison = self.position_comparison.compare_player_to_opponents(player_name, position)
        
        if not comparison:
            print(f"No data available for {player_name} in position {position}")
            return
        
        # All available statistics
        all_stats = [
            ('damage', 'Total Damage'),
            ('kda', 'KDA'),
            ('cs_per_minute', 'CS per minute'),
            ('vision_per_minute', 'Vision per minute'),
            ('damage_per_gold', 'Damage per gold'),
            ('kills', 'Kills'),
            ('deaths', 'Deaths'),
            ('assists', 'Assists')
        ]
        # Prepare data
        stat_names = []
        player_values = []
        opponent_values = []
        raw_player_values = []
        raw_opponent_values = []
        
        for stat_key, stat_display in all_stats:
            if stat_key in comparison['player_stats'] and stat_key in comparison['opponents_stats']:
                stat_names.append(stat_display)
                player_val = comparison['player_stats'][stat_key]
                opponent_val = comparison['opponents_stats'][stat_key]
                
                raw_player_values.append(player_val)
                raw_opponent_values.append(opponent_val)
                
                # Normalize values to 0-100 scale based on max value for this stat
                max_val = max(player_val, opponent_val)
                if max_val > 0:
                    player_values.append((player_val / max_val) * 100)
                    opponent_values.append((opponent_val / max_val) * 100)
                else:
                    player_values.append(0)
                    opponent_values.append(0)
        
        # Create chart with subplots
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
        
        # Chart 1: Normalized values (0-100 scale)
        x = np.arange(len(stat_names))
        width = 0.35
        bars1 = ax1.bar(x - width/2, player_values, width, label=fix_encoding(player_name), color='blue', alpha=0.7)
        bars2 = ax1.bar(x + width/2, opponent_values, width, label='Opponents', color='red', alpha=0.7)
        
        # Add raw values as text on bars
        for i, (bar1, bar2) in enumerate(zip(bars1, bars2)):
            # Player bar
            height1 = bar1.get_height()
            ax1.annotate(f'{raw_player_values[i]:.1f}',
                        xy=(bar1.get_x() + bar1.get_width() / 2, height1),
                        xytext=(0, 3),
                        textcoords="offset points",
                        ha='center', va='bottom', fontsize=8)
            
            # Opponent bar
            height2 = bar2.get_height()
            ax1.annotate(f'{raw_opponent_values[i]:.1f}',
                        xy=(bar2.get_x() + bar2.get_width() / 2, height2),
                        xytext=(0, 3),
                        textcoords="offset points",
                        ha='center', va='bottom', fontsize=8)
        
        ax1.set_xlabel('Statistics')
        ax1.set_ylabel('Normalized Values (0-100)')
        ax1.set_title(f'Normalized comparison: {fix_encoding(player_name)} vs Opponents\n(Raw values shown on bars)')
        ax1.set_xticks(x)
        ax1.set_xticklabels(stat_names, rotation=45, ha='right')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        ax1.set_ylim(0, 110)  # Give some space for text annotations
        
        # Chart 2: Percentage differences
        percentage_diffs = []
        for stat_key, _ in all_stats:
            if stat_key in comparison['differences']:
                percentage_diffs.append(comparison['differences'][stat_key]['percentage_diff'])
            else:
                percentage_diffs.append(0)
        
        colors = ['green' if d > 0 else 'red' for d in percentage_diffs]
        bars = ax2.bar(x, percentage_diffs, color=colors, alpha=0.7)
        
        ax2.set_xlabel('Statistics')
        ax2.set_ylabel('Difference in %')
        ax2.set_title('Percentage differences')
        ax2.set_xticks(x)
        ax2.set_xticklabels(stat_names, rotation=45, ha='right')
        ax2.grid(True, alpha=0.3)
        ax2.axhline(y=0, color='black', linestyle='-', alpha=0.5)
        
        # Add values on bars
        for bar, diff in zip(bars, percentage_diffs):
            height = bar.get_height()
            ax2.annotate(f'{diff:.1f}%',
                        xy=(bar.get_x() + bar.get_width() / 2, height),
                        xytext=(0, 3 if height >= 0 else -15),
                        textcoords="offset points",
                        ha='center', va='bottom' if height >= 0 else 'top')
        
        plt.tight_layout()
        plt.show()
