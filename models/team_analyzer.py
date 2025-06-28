# MODEL: Team analysis logic and business rules for Marmotte Flip vs opponents
from typing import Dict, List, Set, Optional
from collections import defaultdict
import os
import json
from models.game_data import GameData
from models.participant_data import ParticipantData
from utils.utils import fix_encoding

class TeamAnalyzer:
    """Class to analyze Marmotte Flip vs opponents"""
    
    def __init__(self, data_directory: str = "data"):
        self.data_directory = data_directory
        self.target_player = "Aezurly" # Target player to identify the team
        self.marmotte_flip_players: Set[str] = set()
        self.our_players_stats: Dict[str, Dict] = defaultdict(lambda: defaultdict(list))
        self.opponents_stats: Dict[str, Dict] = defaultdict(lambda: defaultdict(list))
        self.games_analyzed = 0
        
    def load_and_analyze_all_games(self):
        """Load and analyze all games to identify Marmotte Flip players and opponents"""
        print("Analyzing games to identify Marmotte Flip team...")

        self._identify_marmotte_flip_players()
        self._collect_statistics()
        
        print(f"Analysis completed: {self.games_analyzed} games analyzed")
        print(f"Marmotte Flip players identified: {len(self.marmotte_flip_players)}")
        print(f"Marmotte Flip players: {', '.join(sorted(self.marmotte_flip_players))}")
    
    def _identify_marmotte_flip_players(self):
        """First pass to identify all Marmotte Flip players"""
        json_files = [f for f in os.listdir(self.data_directory) if f.endswith('.json')]
        
        for filename in json_files:
            file_path = os.path.join(self.data_directory, filename)
            game = GameData(file_path)
            
            if game.data:
                self._process_game_for_team_identification(game)
    
    def _process_game_for_team_identification(self, game: GameData):
        """Process a single game to identify team members"""
        aezurly_participant = self._find_target_player(game)
        if aezurly_participant:
            self._add_teammates_to_team(game, aezurly_participant.get_team())
            
    def _find_target_player(self, game: GameData) -> Optional[ParticipantData]:
        """Find the target player in the game"""
        for participant in game.get_all_participants():
            if fix_encoding(participant.get_name()) == self.target_player:
                return participant
        return None
    
    def _add_teammates_to_team(self, game: GameData, team_id: str):
        """Add all teammates (except target player) to Marmotte Flip players"""
        for participant in game.get_all_participants():
            player_name = fix_encoding(participant.get_name())
            if (participant.get_team() == team_id and 
                player_name != self.target_player):
                self.marmotte_flip_players.add(player_name)
    
    def _collect_statistics(self):
        """Second pass to collect player statistics"""
        json_files = [f for f in os.listdir(self.data_directory) if f.endswith('.json')]
        
        for filename in json_files:
            file_path = os.path.join(self.data_directory, filename)
            game = GameData(file_path)
            
            if game.data:
                self._process_game_for_statistics(game)
    
    def _process_game_for_statistics(self, game: GameData):
        """Process a single game to collect statistics"""
        self.games_analyzed += 1
        game_duration = game.get_game_duration()
        
        for participant in game.get_all_participants():
            player_stats = self._create_player_stats(participant, game_duration)
            self._classify_and_store_player_stats(participant, player_stats)
    
    def _create_player_stats(self, participant: ParticipantData, game_duration: float) -> Dict:
        """Create statistics dictionary for a participant"""
        game_minutes = game_duration / 60 if game_duration > 0 else 1
        
        return {
            'damage': participant.get_total_damage(),
            'damage_per_minute': participant.get_total_damage() / game_minutes,
            'kda': participant.get_kda(),
            'kills': participant.get_kills(),
            'deaths': participant.get_deaths(),
            'assists': participant.get_assists(),
            'cs': participant.get_cs(),
            'cs_per_minute': participant.get_cs() / game_minutes,
            'vision_score': participant.get_vision_score(),
            'vision_per_minute': participant.get_vision_score() / game_minutes,
            'damage_per_gold': participant.get_damage_per_gold(),
            'gold_spent': participant.get_gold_spent(),
            'level': participant.get_level(),
            'champion': participant.get_champion()
        }
        
    def _classify_and_store_player_stats(self, participant: ParticipantData, player_stats: Dict):
        """Classify player as teammate or opponent and store their stats"""
        player_name = fix_encoding(participant.get_name())
        position = participant.get_position()
        
        if self._is_marmotte_flip_player(player_name):
            self.our_players_stats[position][player_name].append(player_stats)
        else:
            self.opponents_stats[position]['opponents'].append(player_stats)
    
    def _is_marmotte_flip_player(self, player_name: str) -> bool:
        """Check if a player is part of Marmotte Flip team"""
        return player_name == self.target_player or player_name in self.marmotte_flip_players
    
    def get_our_players_by_position(self, position: str) -> List[str]:
        """Returns the list of Marmotte Flip players for a given position"""
        if position in self.our_players_stats:
            return list(self.our_players_stats[position].keys())
        return []
    
    def get_player_average_stats(self, player_name: str, position: str) -> Optional[Dict]:
        """Calculates average statistics for a player at a position"""
        if (position in self.our_players_stats and 
            player_name in self.our_players_stats[position]):
            
            games = self.our_players_stats[position][player_name]
            if not games:
                return None
            
            avg_stats = {}
            for stat_name in games[0].keys():
                if stat_name == 'champion':
                    # For champions, take the most played one
                    champions = [game[stat_name] for game in games]
                    avg_stats[stat_name] = max(set(champions), key=champions.count)
                else:
                    # For numerical stats, calculate the average
                    avg_stats[stat_name] = sum(game[stat_name] for game in games) / len(games)
            
            avg_stats['games_played'] = len(games)
            return avg_stats
        return None
    
    def get_opponents_average_stats(self, position: str) -> Optional[Dict]:
        """Calculates average statistics for opponents at a position"""
        if (position in self.opponents_stats and 
            'opponents' in self.opponents_stats[position]):
            
            games = self.opponents_stats[position]['opponents']
            if not games:
                return None
            
            avg_stats = {}
            for stat_name in games[0].keys():
                if stat_name == 'champion':
                    # For champions, take the most played one
                    champions = [game[stat_name] for game in games]
                    avg_stats[stat_name] = max(set(champions), key=champions.count)
                else:
                    # For numerical stats, calculate the average
                    avg_stats[stat_name] = sum(game[stat_name] for game in games) / len(games)
            
            avg_stats['games_played'] = len(games)
            return avg_stats
        return None
    
    def get_all_positions(self) -> List[str]:
        """Returns all available positions"""
        positions = set()
        positions.update(self.our_players_stats.keys())
        positions.update(self.opponents_stats.keys())
        return sorted(list(positions))
    
    def get_marmotte_flip_players_list(self) -> List[str]:
        """Returns the list of all Marmotte Flip team players"""
        return sorted(list(self.marmotte_flip_players))
    
    def get_position_statistics_range(self, position: str) -> Dict[str, Dict[str, float]]:
        """Get the min and max values for each statistic in a position for normalization"""
        all_players_stats = []
        
        # Get our players stats
        if position in self.our_players_stats:
            for player_name, player_games in self.our_players_stats[position].items():
                for game_stats in player_games:
                    all_players_stats.append(game_stats)
        
        # Get opponents stats  
        if position in self.opponents_stats:
            for game_stats in self.opponents_stats[position]['opponents']:
                all_players_stats.append(game_stats)
        
        if not all_players_stats:
            return {}
        
        # Calculate min/max for each metric (using per-minute values)
        stats_ranges = {}
        
        # Define the metrics we want to analyze (using per-minute versions)
        metrics = ['kills', 'deaths', 'assists', 'damage_per_minute', 'cs_per_minute', 'vision_per_minute', 'kda']
        
        for metric in metrics:
            values = []
            for stats in all_players_stats:
                if metric in stats:
                    values.append(stats[metric])
            
            if values:
                stats_ranges[metric] = {
                    'min': min(values),
                    'max': max(values),
                    'range': max(values) - min(values) if max(values) != min(values) else 1
                }
        
        return stats_ranges
    
    def normalize_stats_to_percentage(self, stats: Dict, position: str) -> Dict[str, float]:
        """Convert stats to normalized percentages (0-100) based on position ranges"""
        ranges = self.get_position_statistics_range(position)
        normalized_stats = {}
        
        # Metrics that are "higher is better" 
        higher_is_better = ['kills', 'assists', 'damage_per_minute', 'cs_per_minute', 'vision_per_minute', 'kda']
        # Metrics that are "lower is better"
        lower_is_better = ['deaths']
        
        for metric in higher_is_better:
            if metric in stats and metric in ranges:
                value = stats[metric]
                min_val = ranges[metric]['min']
                max_val = ranges[metric]['max']
                
                if max_val != min_val:
                    # For "higher is better", 0% = min, 100% = max
                    percentage = ((value - min_val) / (max_val - min_val)) * 100
                    normalized_stats[metric] = max(0, min(100, percentage))
                else:
                    normalized_stats[metric] = 50  # If all values are the same
        
        for metric in lower_is_better:
            if metric in stats and metric in ranges:
                value = stats[metric]
                min_val = ranges[metric]['min']
                max_val = ranges[metric]['max']
                
                if max_val != min_val:
                    # For "lower is better", 0% = max, 100% = min (inverted)
                    percentage = ((max_val - value) / (max_val - min_val)) * 100
                    normalized_stats[metric] = max(0, min(100, percentage))
                else:
                    normalized_stats[metric] = 50  # If all values are the same
        
        return normalized_stats
    
    def get_team_average_stats_with_per_minute(self, position: str) -> Optional[Dict]:
        """Get average stats for our team at a position, including per-minute metrics"""
        our_players = self.get_our_players_by_position(position)
        our_player_stats_list = []
        
        for player in our_players:
            player_stats = self.get_player_average_stats(player, position)
            if player_stats:
                our_player_stats_list.append(player_stats)
        
        if not our_player_stats_list:
            return None
        
        # Calculate averages including per-minute metrics
        avg_stats = {
            'kills': sum(stats.get('kills', 0) for stats in our_player_stats_list) / len(our_player_stats_list),
            'deaths': sum(stats.get('deaths', 0) for stats in our_player_stats_list) / len(our_player_stats_list),
            'assists': sum(stats.get('assists', 0) for stats in our_player_stats_list) / len(our_player_stats_list),
            'damage_per_minute': sum(stats.get('damage_per_minute', 0) for stats in our_player_stats_list) / len(our_player_stats_list),
            'cs_per_minute': sum(stats.get('cs_per_minute', 0) for stats in our_player_stats_list) / len(our_player_stats_list),
            'vision_per_minute': sum(stats.get('vision_per_minute', 0) for stats in our_player_stats_list) / len(our_player_stats_list),
            'kda': sum(stats.get('kda', 0) for stats in our_player_stats_list) / len(our_player_stats_list)
        }
        
        return avg_stats
    
    def get_opponents_average_stats_with_per_minute(self, position: str) -> Optional[Dict]:
        """Get average stats for opponents at a position, including per-minute metrics"""
        if position in self.opponents_stats:
            games = self.opponents_stats[position]['opponents']
            if not games:
                return None
            
            avg_stats = {
                'kills': sum(game.get('kills', 0) for game in games) / len(games),
                'deaths': sum(game.get('deaths', 0) for game in games) / len(games),
                'assists': sum(game.get('assists', 0) for game in games) / len(games),
                'damage_per_minute': sum(game.get('damage_per_minute', 0) for game in games) / len(games),
                'cs_per_minute': sum(game.get('cs_per_minute', 0) for game in games) / len(games),
                'vision_per_minute': sum(game.get('vision_per_minute', 0) for game in games) / len(games),
                'kda': sum(game.get('kda', 0) for game in games) / len(games)
            }
            
            return avg_stats
        return None
    
    def get_position_comparison_with_percentages(self, position: str) -> Optional[Dict]:
        """Get position comparison data with normalized percentages"""
        our_stats = self.get_team_average_stats_with_per_minute(position)
        opponent_stats = self.get_opponents_average_stats_with_per_minute(position)
        
        if not our_stats or not opponent_stats:
            return None
        
        # Normalize both to percentages
        our_normalized = self.normalize_stats_to_percentage(our_stats, position)
        opponent_normalized = self.normalize_stats_to_percentage(opponent_stats, position)
        
        return {
            'our_stats_raw': our_stats,
            'opponent_stats_raw': opponent_stats,
            'our_stats_normalized': our_normalized,
            'opponent_stats_normalized': opponent_normalized,
            'position': position
        }
    
    def get_player_comparison_with_percentages(self, player_name: str, position: str) -> Optional[Dict]:
        """Get individual player comparison data with normalized percentages"""
        # Get individual player stats
        player_stats = self.get_player_average_stats(player_name, position)
        if not player_stats:
            return None
        
        # Get opponent stats for comparison
        opponent_stats = self.get_opponents_average_stats_with_per_minute(position)
        if not opponent_stats:
            return None
        
        # Normalize both to percentages
        player_normalized = self.normalize_stats_to_percentage(player_stats, position)
        opponent_normalized = self.normalize_stats_to_percentage(opponent_stats, position)
        
        return {
            'our_stats_raw': player_stats,
            'opponent_stats_raw': opponent_stats,
            'our_stats_normalized': player_normalized,
            'opponent_stats_normalized': opponent_normalized,
            'position': position,
            'player_name': player_name
        }
