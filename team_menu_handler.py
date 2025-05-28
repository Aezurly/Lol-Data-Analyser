from rich.panel import Panel
from rich.prompt import Prompt
from team_analyzer import TeamAnalyzer
from position_comparison import PositionComparison
from team_visualizer import TeamVisualizer
from utils import fix_encoding

class TeamMenuHandler:
    """Menu handler for Aezurly's team analysis"""
    
    # Constants
    PROMPT_PLAYER_NAME = "Enter player name"
    PROMPT_POSITION = "Enter position (TOP (1), JUNGLE (2), MIDDLE (3), BOTTOM (4), UTILITY (5))"
    
    def __init__(self, console):
        self.console = console
        self.team_analyzer = None
        self.position_comparison = None
        self.team_visualizer = None
        self.setup_command_map()
    
    def initialize_analyzers(self):
        """Initialize team analyzers"""
        if not self.team_analyzer:
            self.console.print("[yellow]Loading and analyzing team data...[/yellow]")
            self.team_analyzer = TeamAnalyzer("data")
            self.team_analyzer.load_and_analyze_all_games()
            self.position_comparison = PositionComparison(self.team_analyzer, self.console)
            self.team_visualizer = TeamVisualizer(self.team_analyzer)
    
    def display_team_menu(self):
        """Display team analysis menu"""
        menu_panel = Panel.fit(
            "[bold cyan]Team Analysis - Aezurly & Teammates vs Opponents[/bold cyan]\n\n"
            "[1] View Aezurly's team (identified teammates)\n"
            "[2] Team summary by position\n"
            "[3] Compare specific player to opponents\n"
            "[4] Position overview\n"
            "[5] Radar chart - Player vs opponents comparison\n"
            "[6] Team performance chart\n"
            "[7] Detailed player comparison\n"
            "[8] Compare all players at a position\n"
            "[9] Back to main menu",
            title="[bold]Team Analysis Menu[/bold]",
            border_style="cyan"
        )
        self.console.print(menu_panel)
    
    def show_team_members(self):
        """Display all Aezurly's team members"""
        self.initialize_analyzers()
        teammates = self.team_analyzer.get_marmotte_flip_players_list()
        
        self.console.print(f"\n[bold green]Aezurly's Team ({len(teammates) + 1} total players):[/bold green]")
        self.console.print("[cyan]• Aezurly[/cyan] (target player)")
        
        for teammate in teammates:
            self.console.print(f"[cyan]• {fix_encoding(teammate)}[/cyan]")
        
        self.console.print(f"\n[dim]Based on analysis of {self.team_analyzer.games_analyzed} games[/dim]")
    
    def show_team_summary(self):
        """Display team summary by position"""
        self.initialize_analyzers()
        self.position_comparison.display_team_summary()
    
    def compare_specific_player(self):
        """Compare a specific player to opponents"""
        self.initialize_analyzers()
        
        # Display available positions
        positions = self.team_analyzer.get_all_positions()
        self.console.print(f"\n[yellow]Available positions: {', '.join(positions)}[/yellow]")
        
        position = Prompt.ask(self.PROMPT_POSITION).upper()
        
        if position not in positions:
            self.console.print(f"[red]Position '{position}' not found[/red]")
            return
        
        # Display our players at this position
        our_players = self.team_analyzer.get_our_players_by_position(position)
        
        if not our_players:
            self.console.print(f"[red]No players found at position {position}[/red]")
            return
        
        self.console.print(f"\n[yellow]Our players at {position}: {', '.join([fix_encoding(p) for p in our_players])}[/yellow]")
        
        player_name = Prompt.ask(self.PROMPT_PLAYER_NAME)
        
        if player_name not in our_players:
            self.console.print(f"[red]Player '{player_name}' not found at position {position}[/red]")
            return
        
        self.position_comparison.display_player_comparison(player_name, position)
    
    def show_position_overview(self):
        """Display position overview"""
        self.initialize_analyzers()
        
        positions = self.team_analyzer.get_all_positions()
        self.console.print(f"\n[yellow]Available positions: {', '.join(positions)}[/yellow]")
        
        position = Prompt.ask(self.PROMPT_POSITION).upper()
        
        if position not in positions:
            self.console.print(f"[red]Position '{position}' not found[/red]")
            return
        
        self.position_comparison.display_position_overview(position)
    
    def plot_radar_comparison(self):
        """Create radar chart to compare a player"""
        self.initialize_analyzers()
        
        positions = self.team_analyzer.get_all_positions()
        self.console.print(f"\n[yellow]Available positions: {', '.join(positions)}[/yellow]")
        
        position = Prompt.ask(self.PROMPT_POSITION).upper()
        
        if position not in positions:
            self.console.print(f"[red]Position '{position}' not found[/red]")
            return
        
        our_players = self.team_analyzer.get_our_players_by_position(position)
        
        if not our_players:
            self.console.print(f"[red]No players found at position {position}[/red]")
            return
        player_name = Prompt.ask(self.PROMPT_PLAYER_NAME)
        
        if player_name not in our_players:
            self.console.print(f"[red]Player '{player_name}' not found at position {position}[/red]")
            return
        
        self.team_visualizer.plot_position_comparison_radar(player_name, position)
    
    def plot_team_performance(self):
        """Display team performance chart"""
        self.initialize_analyzers()
        self.team_visualizer.plot_team_performance_overview()
    
    def plot_detailed_comparison(self):
        """Display detailed player comparison"""
        self.initialize_analyzers()
        
        positions = self.team_analyzer.get_all_positions()
        self.console.print(f"\n[yellow]Available positions: {', '.join(positions)}[/yellow]")
        
        position = Prompt.ask(self.PROMPT_POSITION).upper()
        
        if position not in positions:
            self.console.print(f"[red]Position '{position}' not found[/red]")
            return
        
        our_players = self.team_analyzer.get_our_players_by_position(position)
        
        if not our_players:
            self.console.print(f"[red]No players found at position {position}[/red]")
            return
        player_name = Prompt.ask(self.PROMPT_PLAYER_NAME)
        
        if player_name not in our_players:
            self.console.print(f"[red]Player '{player_name}' not found at position {position}[/red]")
            return
        
        self.team_visualizer.plot_detailed_comparison(player_name, position)
    
    def plot_all_players_position(self):
        """Compare all players at a position"""
        self.initialize_analyzers()
        
        positions = self.team_analyzer.get_all_positions()
        self.console.print(f"\n[yellow]Available positions: {', '.join(positions)}[/yellow]")
        
        position = Prompt.ask(self.PROMPT_POSITION).upper()
        
        if position not in positions:
            self.console.print(f"[red]Position '{position}' not found[/red]")
            return
        
        self.team_visualizer.plot_all_players_at_position(position)
    
    def back_to_main_menu(self):
        """Back to main menu"""
        return False
    
    def setup_command_map(self):
        """Set up command mapping"""
        self.command_map = {
            "1": self.show_team_members,
            "2": self.show_team_summary,
            "3": self.compare_specific_player,
            "4": self.show_position_overview,
            "5": self.plot_radar_comparison,
            "6": self.plot_team_performance,
            "7": self.plot_detailed_comparison,
            "8": self.plot_all_players_position,
            "9": self.back_to_main_menu
        }
    
    def get_user_choice(self):
        """Get user choice"""
        return Prompt.ask("Your choice", choices=list(self.command_map.keys()))
    
    def execute_choice(self, choice):
        """Execute user choice"""
        return self.command_map[choice]()
    
    def run_menu_loop(self):
        """Run team analysis menu loop"""
        while True:
            self.display_team_menu()
            choice = self.get_user_choice()
            
            result = self.execute_choice(choice)
            if result is False:  # Signal to return to main menu
                break
            
            # Pause before continuing
            self.console.print("\n[dim]Press Enter to continue...[/dim]")
            input()
