# MODEL: Centralized team management service
"""
Centralized service for team-related operations to reduce code duplication
"""
from typing import List, Dict, Optional, Tuple
from constants import POSITIONS, TARGET_PLAYER
from utils.utils import normalize_player_name, get_position_display_name, get_team_players_summary


class TeamService:
    """Centralized service for team operations and data management"""
    
    def __init__(self, team_analyzer=None):
        self.team_analyzer = team_analyzer
        self._marmotte_flip_players = None
    
    def get_marmotte_flip_players(self) -> List[str]:
        """Get list of all Marmotte Flip players (normalized names)"""
        if self._marmotte_flip_players is None and self.team_analyzer:
            raw_players = self.team_analyzer.get_marmotte_flip_players_list()
            if TARGET_PLAYER not in raw_players:
                raw_players.append(TARGET_PLAYER)
            self._marmotte_flip_players = [normalize_player_name(p) for p in raw_players]
        return self._marmotte_flip_players or []
    
    def get_team_players_by_position(self) -> Dict[str, List[str]]:
        """Get all team players organized by position with normalized names"""
        if not self.team_analyzer:
            return {}
        return get_team_players_summary(self.team_analyzer)
    
    def get_player_options_for_ui(self) -> List[Tuple[str, str, str]]:
        """Get player options formatted for UI display: (display_name, position, original_name)"""
        options = []
        team_players = self.get_team_players_by_position()
        
        for position, players in team_players.items():
            for normalized_name in players:
                # Find original name from analyzer
                original_name = self._find_original_player_name(normalized_name, position)
                display_name = f"{normalized_name} ({get_position_display_name(position, short=True)})"
                options.append((display_name, position, original_name))
        
        return sorted(options)
    
    def _find_original_player_name(self, normalized_name: str, position: str) -> str:
        """Find the original player name from analyzer data"""
        if not self.team_analyzer:
            return normalized_name
            
        original_players = self.team_analyzer.get_our_players_by_position(position)
        for original in original_players:
            if normalize_player_name(original) == normalized_name:
                return original
        return normalized_name
    
    def get_team_summary_stats(self) -> Dict:
        """Get team-wide summary statistics"""
        if not self.team_analyzer:
            return {}
        
        team_players = self.get_team_players_by_position()
        total_players = sum(len(players) for players in team_players.values())
        
        # Count total performances across all positions
        total_performances = 0
        if hasattr(self.team_analyzer, 'our_players_stats'):
            for position in self.team_analyzer.our_players_stats:
                for player in self.team_analyzer.our_players_stats[position]:
                    total_performances += len(self.team_analyzer.our_players_stats[position][player])
        
        return {
            'total_players': total_players,
            'positions_covered': len(team_players),
            'total_performances': total_performances,
            'games_analyzed': getattr(self.team_analyzer, 'games_analyzed', 0)
        }
    
    def validate_player_selection(self, player_display_name: str, position: str) -> Optional[str]:
        """Validate and return the original player name for analysis"""
        player_options = self.get_player_options_for_ui()
        
        for display_name, pos, original_name in player_options:
            if display_name.startswith(player_display_name.split(' (')[0]) and pos == position:
                return original_name
        
        return None
    
    def get_position_display_name(self, position: str, short: bool = False) -> str:
        """Get formatted position name for display"""
        return get_position_display_name(position, short)
    
    def format_player_name_for_display(self, player_name: str) -> str:
        """Format player name for consistent display"""
        return normalize_player_name(player_name)
