import json
from typing import List, Optional
from participant_data import ParticipantData
from game_data import GameData
from game_vizualizer import GameVisualizer
import matplotlib.pyplot as plt
import sys
from rich.console import Console
from rich.table import Table
from rich.text import Text
from rich.panel import Panel
from rich.prompt import Prompt
from rich.columns import Columns
from colorama import init, Fore, Back, Style

# Initialize colorama for Windows compatibility and rich console
init(autoreset=True)
console = Console()

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

if __name__ == "__main__":
    file_path = "game1.json"
    game = GameData(file_path)

    if game.data:
        console.print(f"[bold cyan]Game version:[/bold cyan] {game.get_version()}")
        console.print(f"[bold cyan]Game duration:[/bold cyan] {game.get_game_duration_formatted()}")
        
        table = Table(title="[bold]Participants[/bold]", show_header=True, header_style="bold magenta")
        table.add_column("Name", style="cyan", width=20)
        table.add_column("Position", style="yellow", width=10)
        table.add_column("Champion", style="green", width=15)
        table.add_column("Damage", style="red", width=10)

        for participant in game.get_all_participants():
            name_style = "blue" if participant.get_team() == "100" else "red"
            table.add_row(
                f"[{name_style}]{participant.get_name()}[/{name_style}]",
                participant.get_position(),
                participant.get_champion(),
                str(participant.get_total_damage())
            )

        console.print(table)

        console.print("\n[bold]Total damage by team:[/bold]")
        console.print(f"[bold blue]Blue Team:[/bold blue] {game.get_team_damage('100')}")
        console.print(f"[bold red]Red Team:[/bold red] {game.get_team_damage('200')}")

        visualizer = GameVisualizer(game.get_all_participants(), game)

        def display_menu():
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
            console.print(menu_panel)

        def handle_position_comparison():
            existing_positions = ["TOP", "JUNGLE", "MIDDLE", "BOTTOM", "UTILITY"]
            console.print("[bold yellow]Choose the position to compare (TOP, JUNGLE, MIDDLE, BOTTOM, UTILITY) or ALL:[/bold yellow]")
            position = Prompt.ask("Enter the position").upper()
            if position == "ALL":
                for pos in existing_positions:
                    visualizer.plot_position_comparison_spider_chart(pos)
            elif position in existing_positions:
                visualizer.plot_position_comparison_spider_chart(position)
            else:
                console.print("[bold red]Invalid position. Please try again.[/bold red]")

        command_map = {
            "1": visualizer.plot_total_damage,
            "2": visualizer.plot_kda,
            "3": visualizer.plot_damage_per_gold,
            "4": visualizer.plot_vision_scores,
            "5": handle_position_comparison,
            "6": lambda: (console.print("[bold green]Closing the program.[/bold green]"), exit())
        }

        while True:
            display_menu()
            choice = Prompt.ask("[bold]Enter your choice number[/bold]")
            action = command_map.get(choice)
            if action:
                action()
            else:
                console.print("[bold red]Invalid choice. Please try again.[/bold red]")
