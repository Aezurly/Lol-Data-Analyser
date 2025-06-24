# VIEW: Handles display of multi-game analysis results and player statistics
from typing import Optional, List
from rich.table import Table
from rich.console import Console
from models.multi_game_analyzer import MultiGameAnalyzer, PlayerStats
from views.terminal.prompt_helpers import PromptHelpers
from utils.utils import fix_encoding

class MultiGameDisplay:
    """Handles display of multi-game analysis results"""
    
    def __init__(self, console: Console, analyzer: MultiGameAnalyzer):
        self.console = console
        self.analyzer = analyzer
        self.prompt_helpers = PromptHelpers(console)
    
    def show_loading_progress(self, message: str):
        """Show loading progress message"""
        self.console.print(f"[bold cyan]{message}[/bold cyan]")
    
    def show_error(self, message: str):
        """Show error message"""
        self.console.print(f"[bold red]{message}[/bold red]")
    
    def show_success(self, message: str):
        """Show success message"""
        self.console.print(f"[bold green]{message}[/bold green]")
    
    def show_warning(self, message: str):
        """Show warning message"""
        self.console.print(f"[yellow]{message}[/yellow]")
    
    def display_analysis_summary(self):
        """Display analysis completion summary"""
        self.console.print(f"\n[bold green]Analysis complete! Processed {self.analyzer.games_analyzed} games.[/bold green]")
        self.console.print(f"[bold cyan]Found {len(self.analyzer.player_stats)} unique players.[/bold cyan]")
    
    def display_player_summary(self, player_name: str) -> Optional[str]:
        """Display summary for a specific player"""
        found_player = self.analyzer.find_player(player_name)
        
        if not found_player:
            return self._get_player_with_selection(player_name)
        
        stats = self.analyzer.get_player_stats(found_player)
        if stats:
            self._display_player_stats(stats)
        return found_player
    
    def _get_player_with_selection(self, player_name: str) -> Optional[str]:
        """Get player with selection interface when not found"""
        self._show_player_not_found_message(player_name)
        return self._handle_player_selection()
    
    def _show_player_not_found_message(self, player_name: str):
        """Display player not found message and available players list"""
        self.console.print(f"[bold red]Player '{player_name}' not found.[/bold red]")
        self.console.print("[bold yellow]Available players:[/bold yellow]")
        
        player_list = sorted(self.analyzer.get_all_players())
        for i, name in enumerate(player_list, 1):
            fixed_name = fix_encoding(name)
            self.console.print(f"  [cyan]{i}. {fixed_name}[/cyan]")
    
    def _handle_player_selection(self) -> Optional[str]:
        """Handle user selection of player from list"""
        player_list = sorted(self.analyzer.get_all_players())
        return self.prompt_helpers.select_from_list(
            player_list, 
            prompt_text="Select a player by number", 
            allow_cancel=True, 
            display_encoding_fix=True
        )
    
    def _display_player_stats(self, stats: PlayerStats):
        """Display formatted player statistics"""
        self.console.print(f"\n[bold cyan]=== {stats.name} - Summary ===[/bold cyan]")
        self.console.print(f"[bold]Games played:[/bold] {stats.games_played}")
        self.console.print(f"[bold]Most played champion:[/bold] [yellow]{stats.get_most_played_champion()}[/yellow]")
        self.console.print(f"[bold]Most played position:[/bold] [yellow]{stats.get_most_played_position()}[/yellow]")
        self.console.print(f"[bold]Average damage per game:[/bold] [green]{stats.get_average_damage():.1f}[/green]")
        self.console.print(f"[bold]Average KDA:[/bold] [green]{stats.get_average_kda():.2f}[/green]")
        self.console.print(f"[bold]Average CS/min:[/bold] [green]{stats.get_average_cs_per_minute():.1f}[/green]")
        self.console.print(f"[bold]Average vision score/min:[/bold] [green]{stats.get_average_vision_score_per_minute():.2f}[/green]")
        self.console.print(f"[bold]Average damage per gold:[/bold] [green]{stats.get_average_damage_per_gold():.2f}[/green]")
    
    def display_all_players_summary(self):
        """Display summary table for all players"""
        table = Table(title=f"All Players Summary ({self.analyzer.games_analyzed} games analyzed)")
        table.add_column("Player", style="cyan", no_wrap=True)
        table.add_column("Games", justify="center", style="white")
        table.add_column("Avg Damage", justify="right", style="green")
        table.add_column("Avg KDA", justify="right", style="yellow")
        table.add_column("Main Champion", style="magenta")
        
        for player_name in sorted(self.analyzer.get_all_players()):
            stats = self.analyzer.get_player_stats(player_name)
            if stats:
                table.add_row(
                    fix_encoding(stats.name),
                    str(stats.games_played),
                    f"{stats.get_average_damage():.1f}",
                    f"{stats.get_average_kda():.2f}",
                    stats.get_most_played_champion()
                )
        
        self.console.print(table)
    
    def display_top_players_by_damage(self, limit: int = 10):
        """Display top players by average damage"""
        top_players = self.analyzer.get_top_players_by_damage(limit)
        
        self.console.print(f"\n[bold]Top {limit} Players by Average Damage:[/bold]")
        for i, (name, damage) in enumerate(top_players, 1):
            fixed_name = fix_encoding(name)
            self.console.print(f"{i}. [cyan]{fixed_name}[/cyan]: [green]{damage:.1f}[/green]")
    
    def display_top_players_by_kda(self, limit: int = 10):
        """Display top players by average KDA"""
        top_players = self.analyzer.get_top_players_by_kda(limit)
        
        self.console.print(f"\n[bold]Top {limit} Players by Average KDA:[/bold]")
        for i, (name, kda) in enumerate(top_players, 1):
            fixed_name = fix_encoding(name)
            self.console.print(f"{i}. [cyan]{fixed_name}[/cyan]: [yellow]{kda:.2f}[/yellow]")
