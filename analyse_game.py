import json
from typing import List, Optional
from participant_data import ParticipantData
from game_data import GameData
from game_vizualizer import GameVisualizer
import matplotlib.pyplot as plt

if __name__ == "__main__":
    file_path = "game1.json"
    game = GameData(file_path)

    if game.data:
        print(f"Version du jeu : {game.get_version()}")
        print(f"Durée de la partie : {game.get_game_duration_formatted()}")

        print("\nParticipants :")
        name_width = 20
        position_width = 10
        champion_width = 15
        damage_width = 10

        for participant in game.get_all_participants():
            print(
                f"{participant.get_name():<{name_width}}"
                f"{participant.get_position():<{position_width}}"
                f"{participant.get_champion():<{champion_width}}"
                f"Dégâts: {participant.get_total_damage():<{damage_width}}"
            )

        print("\nDégâts totaux par équipe :")
        print(f"Équipe Blue : {game.get_team_damage('100')}")
        print(f"Équipe Red : {game.get_team_damage('200')}")

        # Créer une instance de GameVisualizer
        visualizer = GameVisualizer(game.get_all_participants(), game)

        # Permettre à l'utilisateur de choisir quel graphique afficher
        while True:
            print("\nChoisissez un graphique à afficher :")
            print("1. Dégâts totaux infligés par joueur")
            print("2. KDA par joueur")
            print("3. DMG/Gold")
            print("4. Score de vision par joueur")
            print("5. Comparer les positions")
            print("6. Quitter")

            choix = input("Entrez le numéro de votre choix : ")

            command_map = {
                "1": visualizer.plot_total_damage,
                "2": visualizer.plot_kda,
                "3": visualizer.plot_damage_per_gold,
                "4": visualizer.plot_vision_scores,
                "5": lambda: (
                    print("Choisis la position à comparer (TOP, JUNGLE, MIDDLE, BOTTOM, UTILITY):"),
                    (position := input("Entrez la position : ").upper()),
                    visualizer.plot_position_comparison_spider_chart(position)
                    if position in ["TOP", "JUNGLE", "MIDDLE", "BOTTOM", "UTILITY"]
                    else print("Position invalide. Veuillez réessayer.")
                ),
                "6": lambda: print("Clôture du programme.") or exit()
            }

            if choix in command_map:
                command_map[choix]()
            else:
                print("Choix invalide. Veuillez réessayer.")
