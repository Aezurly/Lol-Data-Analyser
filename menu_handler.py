from rich.panel import Panel
from rich.prompt import Prompt

class MenuHandler:
    """Handles menu display and user interactions"""
    
    def __init__(self, console, visualizer):
        self.console = console
        self.visualizer = visualizer
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
        self.console.print("[bold yellow]Choose the position to compare (TOP, JUNGLE, MIDDLE, BOTTOM, UTILITY) or ALL:[/bold yellow]")
        position = Prompt.ask("Enter the position").upper()
        if position == "ALL":
            for pos in existing_positions:
                self.visualizer.plot_position_comparison_spider_chart(pos)
        elif position in existing_positions:
            self.visualizer.plot_position_comparison_spider_chart(position)
        else:
            self.console.print("[bold red]Invalid position. Please try again.[/bold red]")
    
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
        return Prompt.ask("[bold]Enter your choice number[/bold]")
    
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

class MultiGameMenuHandler:
    """Handles multi-game analysis menu display and user interactions"""
    
    def __init__(self, console, analyzer):
        self.console = console
        self.analyzer = analyzer
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
            title="[bold]Multi-Game Analysis[/bold]",
            border_style="cyan"
        )
        self.console.print(menu_panel)
    
    def handle_all_players_summary(self):
        """Handle showing all players summary"""
        self.analyzer.print_all_players_summary()
    
    def handle_specific_player_details(self):
        """Handle showing specific player details"""
        player_name = Prompt.ask("Enter player name")
        self.analyzer.print_player_summary(player_name)
    
    def handle_top_players_by_damage(self):
        """Handle showing top players by average damage"""
        limit = int(Prompt.ask("Enter number of top players to show", default="10"))
        top_players = self.analyzer.get_top_players_by_damage(limit)
        self.console.print(f"\n[bold]Top {limit} Players by Average Damage:[/bold]")
        for i, (name, damage) in enumerate(top_players, 1):
            self.console.print(f"{i}. {name}: {damage:.1f}")
    
    def handle_top_players_by_kda(self):
        """Handle showing top players by average KDA"""
        limit = int(Prompt.ask("Enter number of top players to show", default="10"))
        top_players = self.analyzer.get_top_players_by_kda(limit)
        self.console.print(f"\n[bold]Top {limit} Players by Average KDA:[/bold]")
        for i, (name, kda) in enumerate(top_players, 1):
            self.console.print(f"{i}. {name}: {kda:.2f}")
    
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
        return Prompt.ask("[bold]Enter your choice number[/bold]")
    
    def execute_choice(self, choice):
        """Execute the selected menu choice"""
        action = self.command_map.get(choice)
        if action:
            return action()
        else:
            self.console.print("[bold red]Invalid choice. Please try again.[/bold red]")
            return True  # Continue menu loop
    
    def run_menu_loop(self):
        """Run the multi-game analysis menu loop"""
        while True:
            self.display_multi_game_menu()
            choice = self.get_user_choice()
            should_continue = self.execute_choice(choice)
            if should_continue is False:
                break