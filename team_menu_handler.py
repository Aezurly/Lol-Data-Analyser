from rich.panel import Panel
from rich.prompt import Prompt
from team_analyzer import TeamAnalyzer
from position_comparison import PositionComparison
from team_visualizer import TeamVisualizer
from utils import fix_encoding

class TeamMenuHandler:
    """Gestionnaire de menu pour l'analyse d'équipe d'Aezurly"""
    
    def __init__(self, console):
        self.console = console
        self.team_analyzer = None
        self.position_comparison = None
        self.team_visualizer = None
        self.setup_command_map()
    
    def initialize_analyzers(self):
        """Initialise les analyseurs d'équipe"""
        if not self.team_analyzer:
            self.console.print("[yellow]Chargement et analyse des données d'équipe...[/yellow]")
            self.team_analyzer = TeamAnalyzer("data")
            self.team_analyzer.load_and_analyze_all_games()
            self.position_comparison = PositionComparison(self.team_analyzer, self.console)
            self.team_visualizer = TeamVisualizer(self.team_analyzer)
    
    def display_team_menu(self):
        """Affiche le menu d'analyse d'équipe"""
        menu_panel = Panel.fit(
            "[bold cyan]Analyse d'équipe - Aezurly & Coéquipiers vs Adversaires[/bold cyan]\n\n"
            "[1] Voir l'équipe d'Aezurly (coéquipiers identifiés)\n"
            "[2] Résumé de l'équipe par position\n"
            "[3] Comparer un joueur spécifique aux adversaires\n"
            "[4] Vue d'ensemble d'une position\n"
            "[5] Graphique radar - Comparaison joueur vs adversaires\n"
            "[6] Graphique de performance de l'équipe\n"
            "[7] Comparaison détaillée d'un joueur\n"
            "[8] Comparer tous les joueurs d'une position\n"
            "[9] Retour au menu principal",
            title="[bold]Menu Analyse d'Équipe[/bold]",
            border_style="cyan"
        )
        self.console.print(menu_panel)
    
    def show_team_members(self):
        """Affiche tous les membres de l'équipe d'Aezurly"""
        self.initialize_analyzers()
        teammates = self.team_analyzer.get_marmotte_flip_players_list()
        
        self.console.print(f"\n[bold green]Équipe d'Aezurly ({len(teammates) + 1} joueurs au total):[/bold green]")
        self.console.print(f"[cyan]• Aezurly[/cyan] (joueur cible)")
        
        for teammate in teammates:
            self.console.print(f"[cyan]• {fix_encoding(teammate)}[/cyan]")
        
        self.console.print(f"\n[dim]Basé sur l'analyse de {self.team_analyzer.games_analyzed} jeux[/dim]")
    
    def show_team_summary(self):
        """Affiche le résumé de l'équipe par position"""
        self.initialize_analyzers()
        self.position_comparison.display_team_summary()
    
    def compare_specific_player(self):
        """Compare un joueur spécifique aux adversaires"""
        self.initialize_analyzers()
        
        # Afficher les positions disponibles
        positions = self.team_analyzer.get_all_positions()
        self.console.print(f"\n[yellow]Positions disponibles: {', '.join(positions)}[/yellow]")
        
        position = Prompt.ask("Entrez la position").upper()
        
        if position not in positions:
            self.console.print(f"[red]Position '{position}' non trouvée[/red]")
            return
        
        # Afficher nos joueurs à cette position
        our_players = self.team_analyzer.get_our_players_by_position(position)
        
        if not our_players:
            self.console.print(f"[red]Aucun de nos joueurs trouvé en position {position}[/red]")
            return
        
        self.console.print(f"\n[yellow]Nos joueurs en {position}: {', '.join([fix_encoding(p) for p in our_players])}[/yellow]")
        
        player_name = Prompt.ask("Entrez le nom du joueur")
        
        if player_name not in our_players:
            self.console.print(f"[red]Joueur '{player_name}' non trouvé en position {position}[/red]")
            return
        
        self.position_comparison.display_player_comparison(player_name, position)
    
    def show_position_overview(self):
        """Affiche la vue d'ensemble d'une position"""
        self.initialize_analyzers()
        
        positions = self.team_analyzer.get_all_positions()
        self.console.print(f"\n[yellow]Positions disponibles: {', '.join(positions)}[/yellow]")
        
        position = Prompt.ask("Entrez la position").upper()
        
        if position not in positions:
            self.console.print(f"[red]Position '{position}' non trouvée[/red]")
            return
        
        self.position_comparison.display_position_overview(position)
    
    def plot_radar_comparison(self):
        """Crée un graphique radar pour comparer un joueur"""
        self.initialize_analyzers()
        
        positions = self.team_analyzer.get_all_positions()
        self.console.print(f"\n[yellow]Positions disponibles: {', '.join(positions)}[/yellow]")
        
        position = Prompt.ask("Entrez la position").upper()
        
        if position not in positions:
            self.console.print(f"[red]Position '{position}' non trouvée[/red]")
            return
        
        our_players = self.team_analyzer.get_our_players_by_position(position)
        
        if not our_players:
            self.console.print(f"[red]Aucun de nos joueurs trouvé en position {position}[/red]")
            return
        
        self.console.print(f"\n[yellow]Nos joueurs en {position}: {', '.join([fix_encoding(p) for p in our_players])}[/yellow]")
        
        player_name = Prompt.ask("Entrez le nom du joueur")
        
        if player_name not in our_players:
            self.console.print(f"[red]Joueur '{player_name}' non trouvé en position {position}[/red]")
            return
        
        self.team_visualizer.plot_position_comparison_radar(player_name, position)
    
    def plot_team_performance(self):
        """Affiche le graphique de performance de l'équipe"""
        self.initialize_analyzers()
        self.team_visualizer.plot_team_performance_overview()
    
    def plot_detailed_comparison(self):
        """Affiche une comparaison détaillée d'un joueur"""
        self.initialize_analyzers()
        
        positions = self.team_analyzer.get_all_positions()
        self.console.print(f"\n[yellow]Positions disponibles: {', '.join(positions)}[/yellow]")
        
        position = Prompt.ask("Entrez la position").upper()
        
        if position not in positions:
            self.console.print(f"[red]Position '{position}' non trouvée[/red]")
            return
        
        our_players = self.team_analyzer.get_our_players_by_position(position)
        
        if not our_players:
            self.console.print(f"[red]Aucun de nos joueurs trouvé en position {position}[/red]")
            return
        
        self.console.print(f"\n[yellow]Nos joueurs en {position}: {', '.join([fix_encoding(p) for p in our_players])}[/yellow]")
        
        player_name = Prompt.ask("Entrez le nom du joueur")
        
        if player_name not in our_players:
            self.console.print(f"[red]Joueur '{player_name}' non trouvé en position {position}[/red]")
            return
        
        self.team_visualizer.plot_detailed_comparison(player_name, position)
    
    def plot_all_players_position(self):
        """Compare tous les joueurs d'une position"""
        self.initialize_analyzers()
        
        positions = self.team_analyzer.get_all_positions()
        self.console.print(f"\n[yellow]Positions disponibles: {', '.join(positions)}[/yellow]")
        
        position = Prompt.ask("Entrez la position").upper()
        
        if position not in positions:
            self.console.print(f"[red]Position '{position}' non trouvée[/red]")
            return
        
        self.team_visualizer.plot_all_players_at_position(position)
    
    def back_to_main_menu(self):
        """Retour au menu principal"""
        return False
    
    def setup_command_map(self):
        """Configure la correspondance des commandes"""
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
        """Récupère le choix de l'utilisateur"""
        return Prompt.ask("Votre choix", choices=list(self.command_map.keys()))
    
    def execute_choice(self, choice):
        """Exécute le choix de l'utilisateur"""
        return self.command_map[choice]()
    
    def run_menu_loop(self):
        """Lance la boucle du menu d'analyse d'équipe"""
        while True:
            self.display_team_menu()
            choice = self.get_user_choice()
            
            result = self.execute_choice(choice)
            if result is False:  # Signal pour retourner au menu principal
                break
            
            # Pause avant de continuer
            self.console.print("\n[dim]Appuyez sur Entrée pour continuer...[/dim]")
            input()
