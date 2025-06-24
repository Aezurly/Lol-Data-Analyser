# MODEL: Position comparison logic and statistical calculations
from typing import Dict, List, Optional
from team_analyzer import TeamAnalyzer
from rich.table import Table
from rich.console import Console
from utils import fix_encoding

class PositionComparison:
    """Class to compare performance by position"""
    
    def __init__(self, team_analyzer: TeamAnalyzer, console: Console):
        self.team_analyzer = team_analyzer
        self.console = console
    
    def compare_player_to_opponents(self, player_name: str, position: str) -> Optional[Dict]:
        """Compare a specific player to opponents in the same position"""
        player_stats = self.team_analyzer.get_player_average_stats(player_name, position)
        opponents_stats = self.team_analyzer.get_opponents_average_stats(position)
        
        if not player_stats or not opponents_stats:
            return None
        
        comparison = {
            'player_name': player_name,
            'position': position,
            'player_stats': player_stats,
            'opponents_stats': opponents_stats,
            'differences': {}
        }
        
        # Calculate differences for each statistic
        for stat_name, player_value in player_stats.items():
            if stat_name in opponents_stats and stat_name not in ['champion', 'games_played']:
                opponent_value = opponents_stats[stat_name]
                if opponent_value > 0:
                    percentage_diff = ((player_value - opponent_value) / opponent_value) * 100
                    comparison['differences'][stat_name] = {
                        'absolute_diff': player_value - opponent_value,
                        'percentage_diff': percentage_diff,
                        'is_better': player_value > opponent_value
                    }
        
        return comparison
    
    def _create_comparison_table(self, player_name: str, position: str) -> Table:
        """Create the comparison table with columns"""
        table = Table(title=f"{fix_encoding(player_name)} vs Average of {position} opponents", show_header=True, header_style="bold magenta")
        table.add_column("Statistic", style="cyan", width=20)
        table.add_column(f"{fix_encoding(player_name)}", style="green", width=15)
        table.add_column("Opponents", style="red", width=15)
        table.add_column("Difference", style="yellow", width=15)
        table.add_column("% Diff", style="magenta", width=10)
        return table
    
    def _format_stat_values(self, stat_key: str, player_val: float, opponent_val: float, abs_diff: float) -> tuple:
        """Format statistical values for display"""
        if stat_key in ['damage', 'cs_per_minute']:
            player_str = f"{player_val:.0f}"
            opponent_str = f"{opponent_val:.0f}"
            diff_str = f"{abs_diff:+.0f}"
        else:
            player_str = f"{player_val:.2f}"
            opponent_str = f"{opponent_val:.2f}"
            diff_str = f"{abs_diff:+.2f}"
        return player_str, opponent_str, diff_str
    
    def _populate_table_with_stats(self, table: Table, comparison: Dict):
        """Populate the table with statistical data"""
        main_stats = [
            ('damage', 'Damage'),
            ('kda', 'KDA'),
            ('cs_per_minute', 'CS/min'),
            ('vision_per_minute', 'Vision/min'),
            ('damage_per_gold', 'Damage/Gold')
        ]
        
        for stat_key, stat_display in main_stats:
            if stat_key in comparison['player_stats'] and stat_key in comparison['differences']:
                player_val = comparison['player_stats'][stat_key]
                opponent_val = comparison['opponents_stats'][stat_key]
                diff_data = comparison['differences'][stat_key]
                
                player_str, opponent_str, diff_str = self._format_stat_values(
                    stat_key, player_val, opponent_val, diff_data['absolute_diff']
                )
                
                pct_color = "green" if diff_data['is_better'] else "red"
                pct_str = f"[{pct_color}]{diff_data['percentage_diff']:+.1f}%[/{pct_color}]"
                
                table.add_row(stat_display, player_str, opponent_str, diff_str, pct_str)

    def display_player_comparison(self, player_name: str, position: str):
        """Display the comparison of a player with opponents"""
        comparison = self.compare_player_to_opponents(player_name, position)
        
        if not comparison:
            self.console.print(f"[red]No data available for {player_name} in position {position}[/red]")
            return
            
        self.console.print(f"\n[bold cyan]Comparison: {fix_encoding(player_name)} ({position}) vs Opponents[/bold cyan]")
        
        table = self._create_comparison_table(player_name, position)
        self._populate_table_with_stats(table, comparison)
        self.console.print(table)
        
        # Additional information
        self.console.print(f"\n[dim]Games played by {fix_encoding(player_name)}: {comparison['player_stats']['games_played']}[/dim]")
        self.console.print(f"[dim]Opponent games analyzed: {comparison['opponents_stats']['games_played']}[/dim]")
        self.console.print(f"[dim]Most played champion by {fix_encoding(player_name)}: {comparison['player_stats']['champion']}[/dim]")
    
    def display_position_overview(self, position: str):
        """Display an overview of all our players at a position vs opponents"""
        our_players = self.team_analyzer.get_our_players_by_position(position)
        
        if not our_players:
            self.console.print(f"[red]No players found in position {position}[/red]")
            return
        
        self.console.print(f"\n[bold cyan]Overview of position {position}[/bold cyan]")
        
        for player in our_players:
            comparison = self.compare_player_to_opponents(player, position)
            if comparison:
                # Quick summary
                damage_diff = comparison['differences'].get('damage', {}).get('percentage_diff', 0)
                kda_diff = comparison['differences'].get('kda', {}).get('percentage_diff', 0)
                
                damage_color = "green" if damage_diff > 0 else "red"
                kda_color = "green" if kda_diff > 0 else "red"
                self.console.print(f"  • {fix_encoding(player)}: "
                                 f"Damage [{damage_color}]{damage_diff:+.1f}%[/{damage_color}], "
                                 f"KDA [{kda_color}]{kda_diff:+.1f}%[/{kda_color}]")
    
    def get_best_performers_by_position(self) -> Dict[str, List]:
        """Identify our best players by position based on damage"""
        best_performers = {}
        
        for position in self.team_analyzer.get_all_positions():
            our_players = self.team_analyzer.get_our_players_by_position(position)
            position_performances = []
            
            for player in our_players:
                comparison = self.compare_player_to_opponents(player, position)
                if comparison and 'damage' in comparison['differences']:
                    damage_diff = comparison['differences']['damage']['percentage_diff']
                    position_performances.append((player, damage_diff))
            
            # Sort by damage difference (descending)
            position_performances.sort(key=lambda x: x[1], reverse=True)
            best_performers[position] = position_performances
        
        return best_performers
    
    def display_team_summary(self):
        """Display a team summary with the best performers"""
        self.console.print("\n[bold cyan]Team Summary - Best performers by position[/bold cyan]")
        
        best_performers = self.get_best_performers_by_position()
        
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("Position", style="cyan", width=12)
        table.add_column("Best player", style="green", width=20)
        table.add_column("Damage diff vs opponents", style="yellow", width=25)
        for position, performers in best_performers.items():
            if performers:
                best_player, damage_diff = performers[0]
                diff_color = "green" if damage_diff > 0 else "red"
                diff_str = f"[{diff_color}]{damage_diff:+.1f}%[/{diff_color}]"
                table.add_row(position, fix_encoding(best_player), diff_str)
            else:
                table.add_row(position, "No player", "-")
        
        self.console.print(table)
