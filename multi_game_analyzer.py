import os
import json
from typing import Dict, List, Optional
from collections import defaultdict
from game_data import GameData
from participant_data import ParticipantData

def fix_encoding(text):
    """Fix encoding issues in text (convert from Latin-1 to UTF-8)"""
    if not isinstance(text, str):
        return text
    try:
        return text.encode('latin-1').decode('utf-8')
    except (UnicodeDecodeError, UnicodeEncodeError):
        try:
            return text.encode('windows-1252').decode('utf-8')
        except (UnicodeDecodeError, UnicodeEncodeError):
            return text

class PlayerStats:
    """Class to accumulate and calculate average stats for a player"""
    
    def __init__(self, name: str):
        self.name = fix_encoding(name)  # Fix encoding for player name
        self.games_played = 0
        self.total_damage = 0
        self.total_kills = 0
        self.total_deaths = 0
        self.total_assists = 0
        self.total_cs = 0
        self.total_vision_score = 0
        self.total_gold_spent = 0
        self.total_game_duration = 0
        self.champions_played = defaultdict(int)
        self.positions_played = defaultdict(int)
    
    def add_game_stats(self, participant: ParticipantData, game_duration: int):
        """Add stats from a single game"""
        self.games_played += 1
        self.total_damage += participant.get_total_damage()
        self.total_kills += participant.get_kills()
        self.total_deaths += participant.get_deaths()
        self.total_assists += participant.get_assists()
        self.total_cs += participant.get_cs()
        self.total_vision_score += participant.get_vision_score()
        self.total_gold_spent += participant.get_gold_spent()
        self.total_game_duration += game_duration
        self.champions_played[participant.get_champion()] += 1
        self.positions_played[participant.get_position()] += 1
    
    def get_average_damage(self) -> float:
        """Get average damage per game"""
        return self.total_damage / self.games_played if self.games_played > 0 else 0
    
    def get_average_kda(self) -> float:
        """Get average KDA"""
        avg_deaths = self.total_deaths / self.games_played if self.games_played > 0 else 0
        avg_kills = self.total_kills / self.games_played if self.games_played > 0 else 0
        avg_assists = self.total_assists / self.games_played if self.games_played > 0 else 0
        return (avg_kills + avg_assists) / avg_deaths if avg_deaths > 0 else avg_kills + avg_assists
    
    def get_average_cs_per_minute(self) -> float:
        """Get average CS per minute"""
        total_minutes = self.total_game_duration / 60 if self.total_game_duration > 0 else 0
        return self.total_cs / total_minutes if total_minutes > 0 else 0
    
    def get_average_vision_score_per_minute(self) -> float:
        """Get average vision score per minute"""
        total_minutes = self.total_game_duration / 60 if self.total_game_duration > 0 else 0
        return self.total_vision_score / total_minutes if total_minutes > 0 else 0
    
    def get_average_damage_per_gold(self) -> float:
        """Get average damage per gold spent"""
        return self.total_damage / self.total_gold_spent if self.total_gold_spent > 0 else 0
    
    def get_most_played_champion(self) -> str:
        """Get most played champion"""
        return max(self.champions_played.items(), key=lambda x: x[1])[0] if self.champions_played else "Unknown"
    
    def get_most_played_position(self) -> str:
        """Get most played position"""
        return max(self.positions_played.items(), key=lambda x: x[1])[0] if self.positions_played else "Unknown"

class MultiGameAnalyzer:
    """Class to analyze multiple games and calculate player averages"""
    
    def __init__(self, data_directory: str = "data"):
        self.data_directory = data_directory
        self.player_stats: Dict[str, PlayerStats] = {}
        self.games_analyzed = 0
    
    def load_all_games(self):
        """Load and analyze all games in the data directory"""
        if not os.path.exists(self.data_directory):
            print(f"Data directory '{self.data_directory}' not found.")
            return
        
        json_files = [f for f in os.listdir(self.data_directory) if f.endswith('.json')]
        
        if not json_files:
            print(f"No JSON files found in '{self.data_directory}' directory.")
            return
        
        print(f"Found {len(json_files)} game files. Analyzing...")
        
        for filename in json_files:
            file_path = os.path.join(self.data_directory, filename)
            try:
                game = GameData(file_path)
                if game.data:
                    self._analyze_game(game)
                    self.games_analyzed += 1
                    print(f"Analyzed: {filename}")
                else:
                    print(f"Failed to load: {filename}")
            except Exception as e:
                print(f"Error analyzing {filename}: {e}")
        
        print(f"\nAnalysis complete! Processed {self.games_analyzed} games.")
    
    def _analyze_game(self, game: GameData):
        """Analyze a single game and update player stats"""
        game_duration = game.get_game_duration()
        
        for participant in game.get_all_participants():
            player_name = participant.get_name()
            
            if player_name not in self.player_stats:
                self.player_stats[player_name] = PlayerStats(player_name)
            
            self.player_stats[player_name].add_game_stats(participant, game_duration)
    
    def get_player_stats(self, player_name: str) -> Optional[PlayerStats]:
        """Get stats for a specific player"""
        return self.player_stats.get(player_name)
    
    def get_all_players(self) -> List[str]:
        """Get list of all player names"""
        return list(self.player_stats.keys())
    
    def get_top_players_by_damage(self, limit: int = 10) -> List[tuple]:
        """Get top players by average damage"""
        sorted_players = sorted(
            self.player_stats.items(),
            key=lambda x: x[1].get_average_damage(),
            reverse=True
        )
        return [(name, stats.get_average_damage()) for name, stats in sorted_players[:limit]]
    
    def get_top_players_by_kda(self, limit: int = 10) -> List[tuple]:
        """Get top players by average KDA"""
        sorted_players = sorted(
            self.player_stats.items(),
            key=lambda x: x[1].get_average_kda(),
            reverse=True
        )
        return [(name, stats.get_average_kda()) for name, stats in sorted_players[:limit]]
    
    def print_player_summary(self, player_name: str):
        """Print detailed summary for a specific player"""
        if player_name not in self.player_stats:
            print(f"Player '{player_name}' not found.")
            return
        
        stats = self.player_stats[player_name]
        print(f"\n=== {stats.name} - Summary ===")
        print(f"Games played: {stats.games_played}")
        print(f"Most played champion: {stats.get_most_played_champion()}")
        print(f"Most played position: {stats.get_most_played_position()}")
        print(f"Average damage per game: {stats.get_average_damage():.1f}")
        print(f"Average KDA: {stats.get_average_kda():.2f}")
        print(f"Average CS/min: {stats.get_average_cs_per_minute():.1f}")
        print(f"Average vision score/min: {stats.get_average_vision_score_per_minute():.2f}")
        print(f"Average damage per gold: {stats.get_average_damage_per_gold():.2f}")
    
    def print_all_players_summary(self):
        """Print summary for all players"""
        print(f"\n=== All Players Summary ({self.games_analyzed} games analyzed) ===")
        print(f"{'Player':<20} {'Games':<6} {'Avg Damage':<12} {'Avg KDA':<8} {'Main Champion':<15}")
        print("-" * 70)
        
        for player_name in sorted(self.player_stats.keys()):
            stats = self.player_stats[player_name]
            print(f"{stats.name:<20} {stats.games_played:<6} {stats.get_average_damage():<12.1f} {stats.get_average_kda():<8.2f} {stats.get_most_played_champion():<15}")
