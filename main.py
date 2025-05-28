from game_data import GameData
from game_vizualizer import GameVisualizer
from utils import setup_console
from game_display import GameDisplay
from menu_handler import MenuHandler

def main():
    """Main function to run the game analysis application"""
    # Setup console
    console = setup_console()
    
    # Load game data
    file_path = "game1.json"
    game = GameData(file_path)
    
    if not game.data:
        console.print("[bold red]Error: Could not load game data.[/bold red]")
        return
    
    # Initialize display and visualization components
    game_display = GameDisplay(console)
    visualizer = GameVisualizer(game.get_all_participants(), game)
    menu_handler = MenuHandler(console, visualizer)
    
    # Display game information
    game_display.display_game_info(game)
    game_display.display_participants_table(game.get_all_participants())
    game_display.display_team_damage(game)
    
    # Run the interactive menu
    menu_handler.run_menu_loop()

if __name__ == "__main__":
    main()