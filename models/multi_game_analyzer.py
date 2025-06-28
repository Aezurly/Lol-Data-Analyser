# MODEL: Multi-game analysis logic and player statistics calculation
import os
import json
from typing import Dict, List, Optional
from collections import defaultdict
from models.game_data import GameData
from models.participant_data import ParticipantData
from constants import DATA_DIR, TEAM_1_ID, TEAM_2_ID, UNKNOWN_VALUE
from utils.utils import fix_encoding, normalize_player_name
import unicodedata

class PlayerStats:
    """Class to accumulate and calculate average stats for a player"""
    
    def __init__(self, name: str):
        self.name = normalize_player_name(name)  # Normalize player name for consistent handling
        self.games_played = 0
        self.total_wins = 0
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
        # Champion-specific stats for detailed analysis
        self.champion_stats = defaultdict(lambda: {
            'games': 0, 'wins': 0, 'kills': 0, 'deaths': 0, 'assists': 0
        })
    
    def add_game_stats(self, participant: ParticipantData, game_duration: int):
        """Add stats from a single game"""
        self.games_played += 1
        champion = participant.get_champion()
        is_win = participant.get_win()
        
        if is_win:
            self.total_wins += 1
        self.total_damage += participant.get_total_damage()
        self.total_kills += participant.get_kills()
        self.total_deaths += participant.get_deaths()
        self.total_assists += participant.get_assists()
        self.total_cs += participant.get_cs()
        self.total_vision_score += participant.get_vision_score()
        self.total_gold_spent += participant.get_gold_spent()
        self.total_game_duration += game_duration
        self.champions_played[champion] += 1
        self.positions_played[participant.get_position()] += 1
        
        # Track champion-specific stats
        self.champion_stats[champion]['games'] += 1
        if is_win:
            self.champion_stats[champion]['wins'] += 1
        self.champion_stats[champion]['kills'] += participant.get_kills()
        self.champion_stats[champion]['deaths'] += participant.get_deaths()
        self.champion_stats[champion]['assists'] += participant.get_assists()
    
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
    
    def get_average_damage_per_minute(self) -> float:
        """Get average damage per minute"""
        total_minutes = self.total_game_duration / 60 if self.total_game_duration > 0 else 0
        return self.total_damage / total_minutes if total_minutes > 0 else 0
    
    def get_average_damage_per_gold(self) -> float:
        """Get average damage per gold spent"""
        return self.total_damage / self.total_gold_spent if self.total_gold_spent > 0 else 0
    
    def get_most_played_champion(self) -> str:
        """Get most played champion"""
        return max(self.champions_played.items(), key=lambda x: x[1])[0] if self.champions_played else UNKNOWN_VALUE
    
    def get_most_played_position(self) -> str:
        """Get most played position"""
        position = max(self.positions_played.items(), key=lambda x: x[1])[0]
        if position == "BOTTOM":
            return "ADC"
        if position == "UTILITY":
            return "SUP"
        if position == "JUNGLE":
            return "JGL"
        if position == "MIDDLE":
            return "MID"
        return position if position else UNKNOWN_VALUE
    
    def get_win_rate(self) -> float:
        """Get win rate based on games played"""
        return (self.total_wins / self.games_played) if self.games_played > 0 else 0.0
    
    def get_champion_win_rate(self, champion: str) -> float:
        """Get win rate for a specific champion"""
        if champion in self.champion_stats:
            stats = self.champion_stats[champion]
            return (stats['wins'] / stats['games']) if stats['games'] > 0 else 0.0
        return 0.0
    
    def get_champion_kda(self, champion: str) -> float:
        """Get KDA for a specific champion"""
        if champion in self.champion_stats:
            stats = self.champion_stats[champion]
            deaths = stats['deaths']
            return (stats['kills'] + stats['assists']) / deaths if deaths > 0 else (stats['kills'] + stats['assists'])
        return 0.0

class MultiGameAnalyzer:
    """Class to analyze multiple games and calculate player averages"""
    
    # Constants for column names to avoid duplication
    WIN_RATE_COL = 'Win Rate'
    CS_MIN_COL = 'CS/min'
    VISION_MIN_COL = 'Vision/min'
    DMG_MIN_COL = 'Dmg/min'
    
    def __init__(self, data_directory: str = DATA_DIR):
        self.data_directory = data_directory
        self.player_stats: Dict[str, PlayerStats] = {}
        self.games_analyzed = 0
    def load_all_games(self):
        """Load and analyze all games in the data directory"""
        if not os.path.exists(self.data_directory):
            raise FileNotFoundError(f"Data directory '{self.data_directory}' not found.")
        
        json_files = [f for f in os.listdir(self.data_directory) if f.endswith('.json')]
        
        if not json_files:
            raise FileNotFoundError(f"No JSON files found in '{self.data_directory}' directory.")
        
        for filename in json_files:
            file_path = os.path.join(self.data_directory, filename)
            try:
                game = GameData(file_path)
                if game.data:
                    self._analyze_game(game)
            except Exception as e:
                # Log error but continue processing other files
                print(f"Error analyzing {filename}: {e}")
    
    def _analyze_game(self, game: GameData):
        """Analyze a single game and update player stats"""
        self.games_analyzed += 1
        game_duration = game.get_game_duration()
        
        for participant in game.get_all_participants():
            player_name = normalize_player_name(participant.get_name())
            
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
            reverse=True        )
        return [(name, stats.get_average_kda()) for name, stats in sorted_players[:limit]]
    
    def find_player(self, player_name: str) -> Optional[str]:
        """Find a player by name, handling encoding and accent variations"""
        if player_name in self.player_stats:
            return player_name

        fixed_name = fix_encoding(player_name)
        if fixed_name in self.player_stats:
            return fixed_name
        
        def strip_accents(s):
            return ''.join(c for c in unicodedata.normalize('NFD', s) if unicodedata.category(c) != 'Mn')

        for name in self.player_stats:
            if (strip_accents(name).lower() == strip_accents(player_name).lower() or 
                strip_accents(name).lower() == strip_accents(fixed_name).lower()):
                return name
        return None

    def get_players_by_position(self, position: str) -> List[PlayerStats]:
        """Get all players who play a specific position"""
        return [
            stats for stats in self.player_stats.values()
            if stats.games_played > 0 and stats.get_most_played_position() == position
        ]
    
    def get_active_players(self) -> List[tuple]:
        """Get all players with at least one game played"""
        return [
            (name, stats) for name, stats in self.player_stats.items()
            if stats.games_played > 0
        ]
    
    def search_players(self, search_term: str) -> List[str]:
        """Search for players by name (case-insensitive partial match)"""
        search_term = search_term.lower()
        return [
            player_name for player_name in self.player_stats.keys()
            if search_term in player_name.lower()
        ]
    
    def get_position_averages(self, position: str) -> dict:
        """Calculate average statistics for all players in a position"""
        position_players = self.get_players_by_position(position)
        
        if not position_players:
            return {}
        
        total_players = len(position_players)
        return {
            'winrate': sum(s.get_win_rate() for s in position_players) / total_players,
            'kda': sum(s.get_average_kda() for s in position_players) / total_players,
            'dmg_min': sum(s.get_average_damage_per_minute() for s in position_players) / total_players,
            'cs_min': sum(s.get_average_cs_per_minute() for s in position_players) / total_players,
            'vision_min': sum(s.get_average_vision_score_per_minute() for s in position_players) / total_players
        }
    
    def get_player_position_rank(self, player_name: str, metric: str) -> tuple:
        """Get player's rank in their position for a specific metric"""
        player_stats = self.player_stats.get(player_name)
        if not player_stats:
            return (0, 0)
        
        position = player_stats.get_most_played_position()
        position_players = self.get_players_by_position(position)
        
        if len(position_players) < 2:
            return (1, 1)
        
        # Get metric values and sort
        metric_getter = {
            'winrate': lambda s: s.get_win_rate(),
            'kda': lambda s: s.get_average_kda(),
            'dmg_min': lambda s: s.get_average_damage_per_minute(),
            'cs_min': lambda s: s.get_average_cs_per_minute(),
            'vision_min': lambda s: s.get_average_vision_score_per_minute()
        }
        
        if metric not in metric_getter:
            return (0, 0)
        
        sorted_values = sorted(
            [metric_getter[metric](s) for s in position_players], 
            reverse=True
        )
        
        player_value = metric_getter[metric](player_stats)
        rank = sorted_values.index(player_value) + 1
        
        return (rank, len(position_players))
    
    def get_all_champions_played(self) -> dict:
        """Get all champions played by any player with their players list"""
        all_champions = {}
        
        for player_name, stats in self.player_stats.items():
            if stats.games_played > 0:
                most_played = stats.get_most_played_champion()
                if most_played != UNKNOWN_VALUE:
                    if most_played not in all_champions:
                        all_champions[most_played] = []
                    all_champions[most_played].append({
                        'player': fix_encoding(player_name),
                        'games': stats.champions_played[most_played]
                    })
        
        return all_champions

    def get_champion_analytics(self) -> dict:
        """Get detailed champion analytics with formatted player information"""
        all_champions = {}
        
        for player_name, stats in self.player_stats.items():
            if stats.games_played > 0:
                most_played = stats.get_most_played_champion()
                if most_played != UNKNOWN_VALUE:
                    if most_played not in all_champions:
                        all_champions[most_played] = []
                    
                    player_info = f"{fix_encoding(player_name)} ({stats.champions_played[most_played]} games)"
                    all_champions[most_played].append(player_info)
        
        return all_champions

    def create_player_rankings_data(self) -> list:
        """Create formatted player rankings data for display"""
        active_players = self.get_active_players()
        
        player_stats = []
        for player_name, stats_obj in active_players:
            player_stats.append({
                'Player': fix_encoding(player_name),
                'Position': stats_obj.get_most_played_position(),
                'Most Played': stats_obj.get_most_played_champion(),
                'Games': stats_obj.games_played,
                self.WIN_RATE_COL: round(stats_obj.get_win_rate(), 1),
                'Avg KDA': round(stats_obj.get_average_kda(), 2),
                self.CS_MIN_COL: round(stats_obj.get_average_cs_per_minute(), 1),
                self.DMG_MIN_COL: round(stats_obj.get_average_damage_per_minute(), 1),
                'DMG/Gold': round(stats_obj.get_average_damage_per_gold(), 2),
                self.VISION_MIN_COL: round(stats_obj.get_average_vision_score_per_minute(), 2),
                'Kills/Games': round(stats_obj.total_kills / stats_obj.games_played, 2) if stats_obj.games_played > 0 else 0,
                'Deaths/Games': round(stats_obj.total_deaths / stats_obj.games_played, 2) if stats_obj.games_played > 0 else 0,
            })
        
        return player_stats

    def get_player_champions_data(self, player_name: str) -> list:
        """Get formatted champions data for a specific player"""
        stats = self.player_stats.get(player_name)
        if not stats or not stats.champions_played:
            return []
        
        return [
            {
                'Champion': champion,
                'Games': count,
                self.WIN_RATE_COL: f"{stats.get_champion_win_rate(champion)*100:.1f}%",
                'KDA': f"{stats.get_champion_kda(champion):.2f}"
            }
            for champion, count in stats.champions_played.items()
        ]

    def get_player_summary_metrics(self, player_name: str) -> dict:
        """Get formatted summary metrics for a player"""
        stats = self.player_stats.get(player_name)
        if not stats:
            return {}
        
        return {
            'games_played': stats.games_played,
            'position': stats.get_most_played_position(),
            'most_played_champion': stats.get_most_played_champion(),
            'avg_kda': round(stats.get_average_kda(), 2)
        }

    def get_player_detailed_metrics(self, player_name: str) -> dict:
        """Get formatted detailed metrics for a player"""
        stats = self.player_stats.get(player_name)
        if not stats:
            return {}
        
        return {
            'dmg_per_min': round(stats.get_average_damage_per_minute(), 1),
            'cs_per_min': round(stats.get_average_cs_per_minute(), 1),
            'vision_per_min': round(stats.get_average_vision_score_per_minute(), 2),
            'dmg_per_gold': round(stats.get_average_damage_per_gold(), 2),
            'total_kills': stats.total_kills,
            'total_deaths': stats.total_deaths
        }

    def create_position_comparison_data(self, player_name: str) -> list:
        """Create position comparison data for a player"""
        from utils.predicates import MetricFormatter
        
        player_stats = self.player_stats.get(player_name)
        if not player_stats:
            return []
        
        formatter = MetricFormatter()
        position = player_stats.get_most_played_position()
        averages = self.get_position_averages(position)
        
        if not averages:
            return []
        
        metrics = [
            (self.WIN_RATE_COL, 'winrate', lambda s: s.get_win_rate(), formatter.format_percentage),
            ('KDA', 'kda', lambda s: s.get_average_kda(), formatter.format_decimal),
            ('Damage/min', 'dmg_min', lambda s: s.get_average_damage_per_minute(), lambda x: formatter.format_decimal(x, 1)),
            (self.CS_MIN_COL, 'cs_min', lambda s: s.get_average_cs_per_minute(), lambda x: formatter.format_decimal(x, 1)),
            (self.VISION_MIN_COL, 'vision_min', lambda s: s.get_average_vision_score_per_minute(), formatter.format_decimal)
        ]
        
        comparison_data = []
        for metric_name, metric_key, value_getter, formatter_func in metrics:
            player_value = value_getter(player_stats)
            avg_value = averages[metric_key]
            rank, total = self.get_player_position_rank(player_stats.name, metric_key)
            
            comparison_data.append({
                'Metric': metric_name,
                'Player Value': formatter_func(player_value),
                'Position Average': formatter_func(avg_value),
                'Rank': formatter.format_rank(rank, total),
                'Difference': formatter.format_difference_emoji(player_value, avg_value)
            })
        
        return comparison_data

    def has_sufficient_players_for_comparison(self, player_name: str, min_players: int = 2) -> bool:
        """Check if there are enough players in the position for comparison"""
        player_stats = self.player_stats.get(player_name)
        if not player_stats:
            return False
        
        position = player_stats.get_most_played_position()
        position_players = self.get_players_by_position(position)
        return len(position_players) >= min_players

    def get_all_games_data(self) -> list:
        """Get all game files data sorted by date (most recent first)"""
        if not os.path.exists(self.data_directory):
            return []
        
        json_files = [f for f in os.listdir(self.data_directory) if f.endswith('.json')]
        games_data = []
        
        for filename in json_files:
            file_path = os.path.join(self.data_directory, filename)
            try:
                game = GameData(file_path)
                if game.data:
                    # Use existing GameData methods
                    game_info = {
                        'filename': filename,
                        'file_path': file_path,
                        'game_duration': game.get_game_duration(),
                        'game_duration_formatted': game.get_game_duration_formatted(),
                        'participants_count': len(game.get_all_participants()),
                        'date_string': game.get_date_string(),
                        'version': game.get_version()
                    }
                    
                    # Get teams info using existing methods
                    participants = game.get_all_participants()
                    team1_players = []
                    team2_players = []
                    
                    for participant in participants:
                        player_info = {
                            'name': normalize_player_name(participant.get_name()),
                            'champion': participant.get_champion(),
                            'position': participant.get_position(),
                            'win': participant.get_win(),
                            'team': participant.get_team()
                        }
                        
                        if participant.get_team() == TEAM_1_ID:  # Team 1
                            team1_players.append(player_info)
                        else:  # Team 2
                            team2_players.append(player_info)
                    
                    game_info['team1'] = team1_players
                    game_info['team2'] = team2_players
                    game_info['team1_win'] = team1_players[0]['win'] if team1_players else False
                    
                    # Use existing GameData methods for team stats
                    game_info['team1_kills'] = game.get_team_kills(TEAM_1_ID)
                    game_info['team2_kills'] = game.get_team_kills(TEAM_2_ID)
                    game_info['team1_damage'] = game.get_team_damage(TEAM_1_ID)
                    game_info['team2_damage'] = game.get_team_damage("200")
                    
                    games_data.append(game_info)
                    
            except Exception as e:
                print(f"Error processing {filename}: {e}")
                continue
        
        # Sort by filename (assuming date format in filename) - most recent first
        games_data.sort(key=lambda x: x['filename'], reverse=True)
        return games_data

    def get_game_summary_for_display(self, game_info: dict) -> dict:
        """Format game information for display using existing data"""
        # Get winning team info
        winning_team = 1 if game_info['team1_win'] else 2
        losing_team = 2 if game_info['team1_win'] else 1
        
        return {
            'filename': game_info['filename'],
            'duration': game_info['game_duration_formatted'],
            'participants': game_info['participants_count'],
            'winning_team': winning_team,
            'losing_team': losing_team,
            'team1_players': [p['name'] for p in game_info['team1']],
            'team2_players': [p['name'] for p in game_info['team2']],
            'team1_champions': [p['champion'] for p in game_info['team1']],
            'team2_champions': [p['champion'] for p in game_info['team2']],
            'team1_players_with_champions': [f"{p['champion']} ({p['name']})" for p in game_info['team1']],
            'team2_players_with_champions': [f"{p['champion']} ({p['name']})" for p in game_info['team2']],
            'team1_kills': game_info.get('team1_kills', 0),
            'team2_kills': game_info.get('team2_kills', 0),
            'date_string': game_info['date_string'],
            'file_path': game_info['file_path']
        }
