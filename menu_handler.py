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