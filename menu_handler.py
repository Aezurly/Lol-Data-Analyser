# CONTROLLER: Handles menu display and user interactions for single games
from rich.panel import Panel
from rich.prompt import Prompt
from prompt_helpers import PromptHelpers
from multi_game_display import MultiGameDisplay

class MenuHandler:
    """Handles menu display and user interactions"""
    def __init__(self, console, visualizer):
        self.console = console
        self.visualizer = visualizer
        self.prompt_helpers = PromptHelpers(console)
        self.setup_command_map()
    
    def display_menu(self):
        """Display the main menu"""
        menu_panel = Panel.fit(
            "[bold cyan]Choose a chart to display:[/bold cyan]\n\n"
            "[1] Total damage dealt by player\n"
            "[2] KDA by player\n"
            "[3] DMG/Gold\n"
            "[4] Vision score by player\n"
            "[5] Position comparison radar chart\n"
            "[6] Quit",
            title="[bold]Menu[/bold]",
            border_style="cyan"
        )
        self.console.print(menu_panel)
    
    def handle_position_comparison(self):
        """Handle position comparison chart selection"""
        existing_positions = ["TOP", "JUNGLE", "MIDDLE", "BOTTOM", "UTILITY"]
        position = self.prompt_helpers.get_position_with_display(existing_positions, allow_all=True)
        
        if not position:
            return
            
        if position == "ALL":
            for pos in existing_positions:
                self.visualizer.plot_position_comparison_spider_chart(pos)
        else:
            self.visualizer.plot_position_comparison_spider_chart(position)
    
    def setup_command_map(self):
        """Setup the command mapping for menu choices"""
        self.command_map = {
            "1": self.visualizer.plot_total_damage,
            "2": self.visualizer.plot_kda,
            "3": self.visualizer.plot_damage_per_gold,
            "4": self.visualizer.plot_vision_scores,
            "5": self.handle_position_comparison,
            "6": self.quit_program
        }
    
    def quit_program(self):
        """Handle program exit"""
        self.console.print("[bold green]Closing the program.[/bold green]")
        exit()
    
    def get_user_choice(self):
        """Get user menu choice"""
        return self.prompt_helpers.get_menu_choice(list(self.command_map.keys()), prompt_text="Enter your choice number")
    
    def execute_choice(self, choice):
        """Execute the selected menu choice"""
        action = self.command_map.get(choice)
        if action:
            action()
        else:
            self.console.print("[bold red]Invalid choice. Please try again.[/bold red]")
    
    def run_menu_loop(self):
        """Run the main menu loop"""
        while True:
            self.display_menu()
            choice = self.get_user_choice()
            self.execute_choice(choice)
            self.prompt_helpers.pause_for_user()

class MultiGameMenuHandler:
    """Handles multi-game analysis menu display and user interactions"""
    
    def __init__(self, console, analyzer):
        self.console = console
        self.analyzer = analyzer
        self.display = MultiGameDisplay(console, analyzer)
        self.prompt_helpers = PromptHelpers(console)
        self.setup_command_map()
    
    def display_multi_game_menu(self):
        """Display the multi-game analysis menu"""
        menu_panel = Panel.fit(
            "[bold cyan]Multi-Game Analysis Menu:[/bold cyan]\n\n"
            "[1] Show all players summary\n"
            "[2] Show specific player details\n"
            "[3] Show top players by average damage\n"
            "[4] Show top players by average KDA\n"
            "[5] Back to main menu",
            title="[bold]Multi-Game Analysis[/bold]",            border_style="cyan"
        )
        self.console.print(menu_panel)
    
    def handle_all_players_summary(self):
        """Handle showing all players summary"""
        self.display.display_all_players_summary()
    
    def handle_specific_player_details(self):
        """Handle showing specific player details"""
        player_name = self.prompt_helpers.get_player_name(prompt_text="Enter player name")
        if player_name:
            self.display.display_player_summary(player_name)
    
    def handle_top_players_by_damage(self):
        """Handle showing top players by average damage"""
        limit = self.prompt_helpers.get_number_input("Enter number of top players to show", default="10", min_value=1)
        if limit:
            self.display.display_top_players_by_damage(limit)
    
    def handle_top_players_by_kda(self):
        """Handle showing top players by average KDA"""
        limit = self.prompt_helpers.get_number_input("Enter number of top players to show", default="10", min_value=1)
        if limit:
            self.display.display_top_players_by_kda(limit)
    
    def back_to_main_menu(self):
        """Handle returning to main menu"""
        return False  # Signal to exit the menu loop
    
    def setup_command_map(self):
        """Setup the command mapping for multi-game menu choices"""
        self.command_map = {
            "1": self.handle_all_players_summary,
            "2": self.handle_specific_player_details,
            "3": self.handle_top_players_by_damage,
            "4": self.handle_top_players_by_kda,
            "5": self.back_to_main_menu
        }
    
    def get_user_choice(self):
        """Get user menu choice"""
        return self.prompt_helpers.get_menu_choice(list(self.command_map.keys()), prompt_text="Enter your choice number")
    
    def execute_choice(self, choice):
        """Execute the selected menu choice"""
        action = self.command_map.get(choice)
        if action:
            return action()
        else:
            self.prompt_helpers.display_error("Invalid choice. Please try again.")
            return True  # Continue menu loop
    
    def run_menu_loop(self):
        """Run the multi-game analysis menu loop"""
        while True:
            self.display_multi_game_menu()
            choice = self.get_user_choice()
            should_continue = self.execute_choice(choice)
            if should_continue is False:
                break