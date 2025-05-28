from game_data import GameData
from game_vizualizer import GameVisualizer
from utils import setup_console
from game_display import GameDisplay
from menu_handler import MenuHandler, MultiGameMenuHandler
from multi_game_analyzer import MultiGameAnalyzer
from rich.prompt import Prompt
from rich.panel import Panel

class AppController:
    """Main application controller that orchestrates the game analysis application"""
    
    def __init__(self):
        self.console = setup_console()
    
    def display_main_menu(self):
        """Display the main application menu"""
        menu_panel = Panel.fit(
            "[bold cyan]Game Analysis Tool[/bold cyan]\n\n"
            "[1] Analyze single game\n"
            "[2] Analyze multiple games\n"
            "[3] Exit",
            title="[bold]Main Menu[/bold]",
            border_style="cyan"
        )
        self.console.print(menu_panel)
    
    def analyze_single_game(self):
        """Handle single game analysis"""
        file_path = "data/2025-05-27-02.json"
        game = GameData(file_path)
        
        if not game.data:
            self.console.print("[bold red]Error: Could not load game data.[/bold red]")
            return
        
        game_display = GameDisplay(self.console)
        visualizer = GameVisualizer(game.get_all_participants(), game)
        menu_handler = MenuHandler(self.console, visualizer)
        
        game_display.display_game_info(game)
        game_display.display_participants_table(game.get_all_participants())
        game_display.display_team_damage(game)
        
        menu_handler.run_menu_loop()
    
    def analyze_multiple_games(self):
        """Handle multiple games analysis"""
        analyzer = MultiGameAnalyzer("data")
        analyzer.load_all_games()
        
        if analyzer.games_analyzed == 0:
            self.console.print("[bold red]No games were successfully analyzed.[/bold red]")
            return
        
        multi_game_menu = MultiGameMenuHandler(self.console, analyzer)
        multi_game_menu.run_menu_loop()
    
    def exit_application(self):
        """Handle application exit"""
        self.console.print("[bold green]Goodbye![/bold green]")
        return False  # Signal to exit the main loop
    
    def setup_main_command_map(self):
        """Setup the command mapping for main menu choices"""
        return {
            "1": self.analyze_single_game,
            "2": self.analyze_multiple_games,
            "3": self.exit_application
        }
    
    def get_user_choice(self):
        """Get user menu choice"""
        return Prompt.ask("[bold]Enter your choice number[/bold]")
    
    def execute_main_choice(self, choice):
        """Execute the selected main menu choice"""
        command_map = self.setup_main_command_map()
        action = command_map.get(choice)
        if action:
            return action()
        else:
            self.console.print("[bold red]Invalid choice. Please try again.[/bold red]")
            return True  # Continue main loop
    
    def run(self):
        """Run the main application loop"""
        while True:
            self.display_main_menu()
            choice = self.get_user_choice()
            should_continue = self.execute_main_choice(choice)
            if should_continue is False:
                break
