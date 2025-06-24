# VIEW: Handles console display of game information and participant data
from rich.table import Table
from utils import fix_encoding

class GameDisplay:
    """Handles the display of game information and participant data"""
    
    def __init__(self, console):
        self.console = console
    
    def display_game_info(self, game):
        """Display basic game information"""
        self.console.print(f"[bold cyan]Game version:[/bold cyan] {game.get_version()}")
        self.console.print(f"[bold cyan]Game duration:[/bold cyan] {game.get_game_duration_formatted()}")
    
    def display_participants_table(self, participants):
        """Display participants in a formatted table"""
        table = Table(title="[bold]Participants[/bold]", show_header=True, header_style="bold magenta")
        table.add_column("Name", style="cyan", width=20)
        table.add_column("Position", style="yellow", width=10)
        table.add_column("Champion", style="green", width=15)
        table.add_column("Damage", style="red", width=10)

        for participant in participants:
            name_style = "blue" if participant.get_team() == "100" else "red"
            fixed_name = fix_encoding(participant.get_name())
            table.add_row(
                f"[{name_style}]{fixed_name}[/{name_style}]",
                participant.get_position(),
                participant.get_champion(),
                str(participant.get_total_damage())
            )

        self.console.print(table)
    
    def display_team_damage(self, game):
        """Display total damage by team"""
        self.console.print("\n[bold]Total damage by team:[/bold]")
        self.console.print(f"[bold blue]Blue Team:[/bold blue] {game.get_team_damage('100')}")
        self.console.print(f"[bold red]Red Team:[/bold red] {game.get_team_damage('200')}")