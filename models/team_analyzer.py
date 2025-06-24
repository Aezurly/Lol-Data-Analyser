# MODEL: Team analysis logic and business rules for Marmotte Flip vs opponents
from typing import Dict, List, Set, Optional
from collections import defaultdict
import os
import json
from models.game_data import GameData
from models.participant_data import ParticipantData
from utils import fix_encoding

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
        return {
            'damage': participant.get_total_damage(),
            'kda': participant.get_kda(),
            'kills': participant.get_kills(),
            'deaths': participant.get_deaths(),
            'assists': participant.get_assists(),
            'cs': participant.get_cs(),
            'cs_per_minute': participant.get_cs() / (game_duration / 60) if game_duration > 0 else 0,
            'vision_score': participant.get_vision_score(),
            'vision_per_minute': participant.get_vision_score() / (game_duration / 60) if game_duration > 0 else 0,
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
