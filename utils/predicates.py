# UTILS: Predicates and utility functions for data filtering and validation
"""
Predicates and utility functions to centralize business logic
"""

from typing import Any, Callable


def has_minimum_games(min_games: int = 1) -> Callable:
    """Predicate to check if a player has minimum number of games"""
    def predicate(player_stats) -> bool:
        return player_stats.games_played >= min_games
    return predicate

def is_position(target_position: str) -> Callable:
    """Predicate to check if a player plays a specific position"""
    def predicate(player_stats) -> bool:
        return player_stats.get_most_played_position() == target_position
    return predicate

def name_contains(search_term: str) -> Callable:
    """Predicate to check if player name contains search term (case-insensitive)"""
    def predicate(player_name: str) -> bool:
        return search_term.lower() in player_name.lower()
    return predicate

def champion_is_known() -> Callable:
    """Predicate to check if champion is not 'Unknown'"""
    def predicate(champion_name: str) -> bool:
        return champion_name != "Unknown"
    return predicate

def has_sufficient_position_players(min_players: int = 2) -> Callable:
    """Predicate to check if there are enough players in a position for comparison"""
    def predicate(position_players_count: int) -> bool:
        return position_players_count >= min_players
    return predicate


# Utility functions for formatting and display
class MetricFormatter:
    """Utility class for formatting metrics consistently"""
    
    @staticmethod
    def format_percentage(value: float, decimals: int = 1) -> str:
        """Format a decimal as percentage"""
        return f"{value * 100:.{decimals}f}%"
    
    @staticmethod
    def format_decimal(value: float, decimals: int = 2) -> str:
        """Format a decimal with specified precision"""
        return f"{value:.{decimals}f}"
    
    @staticmethod
    def format_rank(rank: int, total: int) -> str:
        """Format rank as 'rank/total'"""
        return f"{rank}/{total}"
    
    @staticmethod
    def format_difference_emoji(player_value: float, avg_value: float) -> str:
        """Format difference with emoji and percentage"""
        if avg_value == 0:
            return "N/A"
        
        diff = player_value - avg_value
        percentage = (diff / avg_value) * 100
        
        if diff > 0:
            return f"📈 +{percentage:.1f}%"
        elif diff < 0:
            return f"📉 {percentage:.1f}%"
        else:
            return "➡️ 0.0%"


class RankCalculator:
    """Utility class for rank-related calculations"""
    
    @staticmethod
    def get_rank_tier(rank: int, total: int) -> str:
        """Get rank tier (top, middle, bottom third)"""
        if rank <= total / 3:
            return "top"
        elif rank > (2 * total / 3):
            return "bottom"
        else:
            return "middle"
    
    @staticmethod
    def get_rank_color_style(rank: int, total: int) -> str:
        """Get CSS style for rank coloring"""
        tier = RankCalculator.get_rank_tier(rank, total)
        
        styles = {
            "top": 'background-color: #d4edda; color: #155724; font-weight: bold',
            "bottom": 'background-color: #f8d7da; color: #721c24; font-weight: bold',
            "middle": 'background-color: #fff3cd; color: #856404; font-weight: bold'
        }
        
        return styles.get(tier, '')
    
    @staticmethod
    def get_difference_color_style(difference_text: str) -> str:
        """Get CSS style for difference coloring"""
        if difference_text == "N/A":
            return 'color: gray'
        
        if '📈' in difference_text:
            return 'background-color: #d4edda; color: #155724; font-weight: bold'
        elif '📉' in difference_text:
            return 'background-color: #f8d7da; color: #721c24; font-weight: bold'
        elif '➡️' in difference_text:
            return 'background-color: #e2e3e5; color: #383d41'
        else:
            return ''


class DataFrameStyler:
    """Utility class for styling DataFrames consistently"""
    
    @staticmethod
    def apply_comparison_styling(df):
        """Apply color styling to comparison DataFrames"""
        def color_difference(val):
            return RankCalculator.get_difference_color_style(val)
        
        def color_rank(val):
            if '/' not in val:
                return ''
            
            try:
                rank, total = val.split('/')
                return RankCalculator.get_rank_color_style(int(rank), int(total))
            except ValueError:
                return ''
        
        styled_df = df.style.map(color_difference, subset=['Difference'])
        styled_df = styled_df.map(color_rank, subset=['Rank'])
        return styled_df

    @staticmethod
    def get_win_rate_column_config():
        """Get column configuration for win rate display"""
        import streamlit as st
        from models.multi_game_analyzer import MultiGameAnalyzer
        return {
            MultiGameAnalyzer.WIN_RATE_COL: st.column_config.NumberColumn(
                MultiGameAnalyzer.WIN_RATE_COL,
                help="Win rate percentage",
                format="percent"
            )
        }

    @staticmethod
    def get_comparison_column_config():
        """Get column configuration for comparison tables"""
        import streamlit as st
        return {
            "Metric": st.column_config.TextColumn("Metric", width="small"),
            "Player Value": st.column_config.TextColumn("Your Value", width="small"),
            "Position Average": st.column_config.TextColumn("Position Avg", width="small"),
            "Rank": st.column_config.TextColumn("Rank", width="small"),
            "Difference": st.column_config.TextColumn("Difference", width="small")
        }


class DisplayHelpers:
    """Helper functions for UI display logic"""
    
    @staticmethod
    def get_sort_options():
        """Get available sort options for player rankings"""
        from models.multi_game_analyzer import MultiGameAnalyzer
        return [MultiGameAnalyzer.WIN_RATE_COL, 'Avg KDA', 'Games', 
                MultiGameAnalyzer.DMG_MIN_COL, MultiGameAnalyzer.CS_MIN_COL, 
                MultiGameAnalyzer.VISION_MIN_COL]

    @staticmethod
    def create_tabs():
        """Create the main tabs for the global stats application"""
        import streamlit as st
        return st.tabs(["📋 Player Table", "🎯 Champion Analytics"])

    @staticmethod
    def get_search_placeholder():
        """Get placeholder text for search input"""
        return "Enter player name..."

    @staticmethod
    def format_search_results_message(count: int) -> str:
        """Format the search results count message"""
        return f"Found {count} matching player(s)"

    @staticmethod
    def format_no_results_message(search_term: str) -> str:
        """Format the no results message"""
        return f"No players found matching '{search_term}'"

    @staticmethod
    def format_position_comparison_message(position: str, count: int) -> str:
        """Format position comparison message"""
        return f"Compared to {count} players in **{position}** position:"


class ValidationHelpers:
    """Helper functions for validation logic"""
    
    @staticmethod
    def validate_player_exists(analyzer, player_name: str) -> bool:
        """Validate that a player exists in the analyzer"""
        return player_name in analyzer.player_stats

    @staticmethod
    def validate_games_analyzed(analyzer) -> bool:
        """Validate that games have been analyzed"""
        return analyzer.games_analyzed > 0

    @staticmethod
    def validate_champions_data(champions_dict: dict) -> bool:
        """Validate that champions data is available"""
        return bool(champions_dict)

    @staticmethod
    def validate_player_stats_exist(stats) -> bool:
        """Validate that player stats exist"""
        return stats is not None
