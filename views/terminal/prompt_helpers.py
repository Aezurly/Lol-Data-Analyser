# VIEW: Centralized helper for user prompts and console interactions
from rich.prompt import Prompt
from rich.console import Console
from typing import List, Optional, Dict, Union
from utils.utils import fix_encoding

class PromptHelpers:
    """Centralized helper class for user prompts and interactions"""
    
    def __init__(self, console: Console):
        self.console = console
        
        # Common prompt constants
        self.POSITION_OPTIONS = ["TOP", "JUNGLE", "MIDDLE", "BOTTOM", "UTILITY"]
        self.POSITION_MAP = {
            "1": "TOP",
            "2": "JUNGLE", 
            "3": "MIDDLE",
            "4": "BOTTOM",
            "5": "UTILITY"
        }
    
    def get_player_name(self, available_players: Optional[List[str]] = None, prompt_text: str = "Enter player name") -> Optional[str]:
        """
        Get a player name from user with optional validation against available players
        
        Args:
            available_players: List of available player names for validation
            prompt_text: Custom prompt text
            
        Returns:
            Selected player name or None if cancelled
        """
        if available_players:
            self.console.print(f"\n[yellow]Available players: {', '.join([fix_encoding(p) for p in available_players])}[/yellow]")
        
        player_name = Prompt.ask(prompt_text)
        
        if available_players and player_name not in available_players:
            self.console.print(f"[red]Player '{player_name}' not found in the available list[/red]")
            return self._handle_player_selection_from_list(available_players)
        
        return player_name
    
    def get_position(self, available_positions: Optional[List[str]] = None, allow_numbers: bool = True) -> Optional[str]:
        """
        Get a position from user with validation
        
        Args:
            available_positions: List of available positions for validation
            allow_numbers: Whether to allow numeric input (1-5)
            
        Returns:
            Selected position in uppercase or None if invalid
        """
        positions_display = available_positions or self.POSITION_OPTIONS
        
        if allow_numbers:
            self.console.print(f"\n[yellow]Available positions: {', '.join(positions_display)}[/yellow]")
            self.console.print("[dim]You can enter the position name or number (1=TOP, 2=JUNGLE, 3=MIDDLE, 4=BOTTOM, 5=UTILITY)[/dim]")
            prompt_text = "Enter position (name or number)"
        else:
            self.console.print(f"\n[yellow]Available positions: {', '.join(positions_display)}[/yellow]")
            prompt_text = "Enter position"
        
        user_input = Prompt.ask(prompt_text).strip()
        
        # Handle numeric input
        if allow_numbers and user_input in self.POSITION_MAP:
            position = self.POSITION_MAP[user_input]
        else:
            position = user_input.upper()
        
        # Validate against available positions
        valid_positions = available_positions or self.POSITION_OPTIONS
        if position not in valid_positions:
            self.console.print(f"[red]Position '{position}' not found in available positions[/red]")
            return None
            
        return position
    
    def get_menu_choice(self, choices: List[str], prompt_text: str = "Enter your choice number") -> str:
        """
        Get a menu choice from user with validation
        
        Args:
            choices: List of valid choice options
            prompt_text: Custom prompt text
            
        Returns:
            Selected choice
        """
        return Prompt.ask(f"[bold]{prompt_text}[/bold]", choices=choices)
    
    def get_number_input(self, prompt_text: str, default: Optional[str] = None, min_value: Optional[int] = None, max_value: Optional[int] = None) -> Optional[int]:
        """
        Get a numeric input from user with validation
        
        Args:
            prompt_text: Prompt text to display
            default: Default value if user presses Enter
            min_value: Minimum allowed value
            max_value: Maximum allowed value
            
        Returns:
            Integer value or None if invalid
        """
        try:
            if default:
                value_str = Prompt.ask(prompt_text, default=str(default))
            else:
                value_str = Prompt.ask(prompt_text)
            
            value = int(value_str)
            
            if min_value is not None and value < min_value:
                self.console.print(f"[red]Value must be at least {min_value}[/red]")
                return None
                
            if max_value is not None and value > max_value:
                self.console.print(f"[red]Value must be at most {max_value}[/red]")
                return None
                
            return value
            
        except ValueError:
            self.console.print("[red]Invalid number. Please enter a valid integer.[/red]")
            return None
    
    def get_yes_no_choice(self, prompt_text: str, default: bool = True) -> bool:
        """
        Get a yes/no choice from user
        
        Args:
            prompt_text: Question to ask the user
            default: Default value (True for yes, False for no)
            
        Returns:
            Boolean result
        """
        default_str = "y" if default else "n"
        choices = ["y", "n", "yes", "no"]
        
        response = Prompt.ask(f"{prompt_text} (y/n)", choices=choices, default=default_str).lower()
        return response in ["y", "yes"]
    
    def select_from_list(self, items: List[str], prompt_text: str = "Select an item", allow_cancel: bool = True, display_encoding_fix: bool = True) -> Optional[str]:
        """
        Display a numbered list and get user selection
        
        Args:
            items: List of items to choose from
            prompt_text: Prompt text to display
            allow_cancel: Whether to allow cancellation
            display_encoding_fix: Whether to apply encoding fix to displayed items
            
        Returns:
            Selected item or None if cancelled
        """
        if not items:
            self.console.print("[red]No items available to select from[/red]")
            return None
        
        self.console.print(f"\n[bold yellow]{prompt_text}:[/bold yellow]")
        
        for i, item in enumerate(items, 1):
            display_item = fix_encoding(item) if display_encoding_fix else item
            self.console.print(f"  [cyan]{i}. {display_item}[/cyan]")
        
        if allow_cancel:
            self.console.print("  [dim]0. Cancel[/dim]")
        
        try:
            max_choice = len(items)
            min_choice = 0 if allow_cancel else 1
            
            choice_str = Prompt.ask(f"\nEnter choice ({min_choice}-{max_choice})")
            choice = int(choice_str)
            
            if choice == 0 and allow_cancel:
                return None
            elif 1 <= choice <= len(items):
                selected = items[choice - 1]
                display_selected = fix_encoding(selected) if display_encoding_fix else selected
                self.console.print(f"[green]Selected: {display_selected}[/green]")
                return selected
            else:
                self.console.print(f"[red]Invalid choice. Please enter a number between {min_choice} and {max_choice}[/red]")
                return None
                
        except ValueError:
            self.console.print("[red]Invalid input. Please enter a number.[/red]")
            return None
    
    def _handle_player_selection_from_list(self, players: List[str]) -> Optional[str]:
        """Handle player selection from a list when direct name entry fails"""
        return self.select_from_list(
            players, 
            prompt_text="Available players - select by number",
            allow_cancel=True,
            display_encoding_fix=True
        )
    
    def confirm_action(self, action_description: str) -> bool:
        """
        Ask user to confirm an action
        
        Args:
            action_description: Description of the action to confirm
            
        Returns:
            True if confirmed, False otherwise
        """
        return self.get_yes_no_choice(f"Are you sure you want to {action_description}?", default=False)
    
    def pause_for_user(self, message: str = "Press Enter to continue...") -> None:
        """
        Pause execution and wait for user to press Enter
        
        Args:
            message: Message to display to user
        """
        self.console.print(f"\n[dim]{message}[/dim]")
        input()
    
    def display_error(self, message: str) -> None:
        """
        Display an error message in consistent formatting
        
        Args:
            message: Error message to display
        """
        self.console.print(f"[bold red]{message}[/bold red]")
    
    def display_warning(self, message: str) -> None:
        """
        Display a warning message in consistent formatting
        
        Args:
            message: Warning message to display
        """
        self.console.print(f"[bold yellow]{message}[/bold yellow]")
    
    def display_success(self, message: str) -> None:
        """
        Display a success message in consistent formatting
        
        Args:
            message: Success message to display
        """
        self.console.print(f"[bold green]{message}[/bold green]")
    
    def get_position_with_display(self, available_positions: Optional[List[str]] = None, allow_all: bool = False) -> Optional[str]:
        """
        Get a position from user with enhanced display including ALL option
        
        Args:
            available_positions: List of available positions for validation
            allow_all: Whether to allow "ALL" as an option
            
        Returns:
            Selected position in uppercase or None if invalid
        """
        positions_display = available_positions or self.POSITION_OPTIONS
        
        if allow_all:
            extended_positions = positions_display + ["ALL"]
            self.console.print(f"\n[yellow]Available positions: {', '.join(positions_display)} or ALL[/yellow]")
        else:
            extended_positions = positions_display
            self.console.print(f"\n[yellow]Available positions: {', '.join(positions_display)}[/yellow]")
        
        self.console.print("[dim]You can enter the position name or number (1=TOP, 2=JUNGLE, 3=MIDDLE, 4=BOTTOM, 5=UTILITY)[/dim]")
        
        user_input = Prompt.ask("Enter position (name or number)").strip()
        
        # Handle numeric input
        if user_input in self.POSITION_MAP:
            position = self.POSITION_MAP[user_input]
        else:
            position = user_input.upper()
        
        # Validate against available positions
        if position not in extended_positions:
            self.display_error(f"Position '{position}' not found in available positions")
            return None
            
        return position
    
    def get_player_name_with_fallback(self, available_players: List[str], prompt_text: str = "Enter player name") -> Optional[str]:
        """
        Get a player name with automatic fallback to selection list if not found
        
        Args:
            available_players: List of available player names
            prompt_text: Custom prompt text
            
        Returns:
            Selected player name or None if cancelled
        """
        # First try direct input
        self.console.print(f"\n[yellow]Available players: {', '.join([fix_encoding(p) for p in available_players])}[/yellow]")
        player_name = Prompt.ask(prompt_text)
        
        if player_name in available_players:
            return player_name
        
        # If not found, show selection list
        self.display_warning(f"Player '{player_name}' not found in the available list")
        return self.select_from_list(
            available_players, 
            prompt_text="Please select from the available players",
            allow_cancel=True,
            display_encoding_fix=True
        )
