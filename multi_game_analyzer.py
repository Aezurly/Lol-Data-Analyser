import os
import json
from typing import Dict, List, Optional
from collections import defaultdict
from game_data import GameData
from participant_data import ParticipantData
import unicodedata
from utils import setup_console
from prompt_helpers import PromptHelpers

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
    
    def __init__(self, data_directory: str = "data", console=None):
        self.data_directory = data_directory
        self.player_stats: Dict[str, PlayerStats] = {}
        self.games_analyzed = 0
        self.console = console if console else setup_console()
        self.prompt_helpers = PromptHelpers(self.console)
    
    def load_all_games(self):
        """Load and analyze all games in the data directory"""
        if not os.path.exists(self.data_directory):
            self.console.print(f"[bold red]Data directory '{self.data_directory}' not found.[/bold red]")
            return
        
        json_files = [f for f in os.listdir(self.data_directory) if f.endswith('.json')]
        
        if not json_files:
            self.console.print(f"[bold red]No JSON files found in '{self.data_directory}' directory.[/bold red]")
            return
        
        self.console.print(f"[bold cyan]Found {len(json_files)} game files. Analyzing...[/bold cyan]")
        
        for filename in json_files:
            file_path = os.path.join(self.data_directory, filename)
            try:
                game = GameData(file_path)
                if game.data:
                    self._analyze_game(game)
                    self.games_analyzed += 1
                    self.console.print(f"[green]Analyzed: {filename}[/green]")
                else:
                    self.console.print(f"[yellow]Failed to load: {filename}[/yellow]")
            except Exception as e:
                self.console.print(f"[red]Error analyzing {filename}: {e}[/red]")
        
        self.console.print(f"\n[bold green]Analysis complete! Processed {self.games_analyzed} games.[/bold green]")
    
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
    
    def print_player_summary(self, player_name: str):
        """Print detailed summary for a specific player"""
        found_player = self._get_player_with_selection(player_name)
        if not found_player:
            return
        
        stats = self.player_stats[found_player]
        self._display_player_stats(stats)
    
    def _get_player_with_selection(self, player_name: str) -> Optional[str]:
        """Find player or let user select from list if not found"""
        found_player = self.find_player(player_name)
        
        if found_player:
            return found_player
        
        self._show_player_not_found_message(player_name)
        return self._handle_player_selection()
    
    def _show_player_not_found_message(self, player_name: str):
        """Display player not found message and available players list"""
        self.console.print(f"[bold red]Player '{player_name}' not found.[/bold red]")
        self.console.print("[bold yellow]Available players:[/bold yellow]")
        
        player_list = sorted(self.player_stats.keys())
        for i, name in enumerate(player_list, 1):
            self.console.print(f"  [cyan]{i}. {name}[/cyan]")
    
    def _handle_player_selection(self) -> Optional[str]:
        """Handle user selection of player from list"""
        player_list = sorted(self.player_stats.keys())
        return self.prompt_helpers.select_from_list(player_list, prompt_text="Select a player by number", allow_cancel=True, display_encoding_fix=True)
    
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
    
    def print_all_players_summary(self):
        """Print summary for all players"""
        from rich.table import Table
        
        table = Table(title=f"All Players Summary ({self.games_analyzed} games analyzed)")
        table.add_column("Player", style="cyan", no_wrap=True)
        table.add_column("Games", justify="center", style="white")
        table.add_column("Avg Damage", justify="right", style="green")
        table.add_column("Avg KDA", justify="right", style="yellow")
        table.add_column("Main Champion", style="magenta")
        
        for player_name in sorted(self.player_stats.keys()):
            stats = self.player_stats[player_name]
            table.add_row(
                stats.name,
                str(stats.games_played),
                f"{stats.get_average_damage():.1f}",
                f"{stats.get_average_kda():.2f}",
                stats.get_most_played_champion()
            )
        
        self.console.print(table)
