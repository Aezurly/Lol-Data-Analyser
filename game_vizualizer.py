from typing import List
from participant_data import ParticipantData
from game_data import GameData
import matplotlib.pyplot as plt


class GameVisualizer:
    """Classe pour générer des graphiques à partir des données de jeu."""
    def __init__(self, participants: List[ParticipantData], game: GameData):
        self.participants = participants
        self.game = game

    def _plot_bar_chart(self, x_labels, y_values, title, xlabel, ylabel, color='skyblue'):
        """Méthode utilitaire pour afficher un graphique en barres."""
        plt.figure(figsize=(10, 6))
        plt.bar(x_labels, y_values, color=color)
        plt.title(title)
        plt.xlabel(xlabel)
        plt.ylabel(ylabel)
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        plt.show()

    def _plot_grouped_bar_chart(self, x_labels, groups, group_labels, title, xlabel, ylabel):
        """Méthode utilitaire pour afficher un graphique en barres groupées."""
        x = range(len(x_labels))
        plt.figure(figsize=(10, 6))
        width = 0.25
        for i, (values, label, color) in enumerate(groups):
            plt.bar([pos + i * width for pos in x], values, width=width, label=label, color=color, align='center')
        plt.title(title)
        plt.xlabel(xlabel)
        plt.ylabel(ylabel)
        plt.xticks([pos + (len(groups) - 1) * width / 2 for pos in x], x_labels, rotation=45, ha='right')
        plt.legend()
        plt.tight_layout()
        plt.show()

    def plot_total_damage(self):
        """Affiche un graphique des dégâts totaux infligés par joueur et leur champion."""
        names_and_champions = [f"{p.get_name()} ({p.get_champion()})" for p in self.participants]
        damages = [p.get_total_damage() for p in self.participants]
        self._plot_bar_chart(
            x_labels=names_and_champions,
            y_values=damages,
            title="Damage done",
            xlabel="Players (Champion)",
            ylabel="Damage"
        )

    def plot_kda(self):
        """Affiche un graphique des KDA (Kills, Deaths, Assists) par joueur."""
        names = self._get_participant_names()
        kills = [p.get_kills() for p in self.participants]
        deaths = [p.get_deaths() for p in self.participants]
        assists = [p.get_assists() for p in self.participants]
        self._plot_grouped_bar_chart(
            x_labels=names,
            groups=[
                (kills, 'Kills', 'green'),
                (deaths, 'Deaths', 'red'),
                (assists, 'Assists', 'blue')
            ],
            group_labels=['Kills', 'Deaths', 'Assists'],
            title="KDA",
            xlabel="Players",
            ylabel="Number"
        )

    def plot_damage_per_gold(self):
        """Affiche un graphique des dégâts par or dépensé par joueur."""
        names = self._get_participant_names()
        damage_per_gold = [p.get_damage_per_gold() for p in self.participants]
        self._plot_bar_chart(
            x_labels=names,
            y_values=damage_per_gold,
            title="DMG/Gold",
            xlabel="Players",
            ylabel="DMG/Gold",
            color='orange'
        )

    def plot_vision_scores(self):
        """Affiche un graphique des scores de vision par joueur."""
        names = self._get_participant_names()
        vision_scores = [p.get_vision_score() for p in self.participants]
        self._plot_bar_chart(
            x_labels=names,
            y_values=vision_scores,
            title="Vision Score",
            xlabel="Players",
            ylabel="Vision Score",
            color='purple'
        )

    def plot_team_damage_distribution(self):
        """Affiche un graphique en camembert de la répartition des dégâts par équipe."""
        team_100_damage = self.game.get_team_damage('100')
        team_200_damage = self.game.get_team_damage('200')
        plt.figure(figsize=(8, 6))
        plt.pie(
            [team_100_damage, team_200_damage],
            labels=["Blue Team", "Red Team"],
            autopct='%1.1f%%',
            colors=['blue', 'red']
        )
        plt.title("Damage Distribution by Team")
        plt.show()
        
    def plot_position_comparison_spider_chart(self, position: str):
        """Affiche un graphique radar pour comparer les deux joueurs d'une position donnée."""
        # Filtrer les participants par position
        position_players = [p for p in self.participants if p.get_position() == position]
        if len(position_players) != 2:
            raise ValueError(f"Expected exactly 2 players for position {position}, but found {len(position_players)}.")

        # Récupérer les statistiques à comparer
        stats_labels = ['KDA', 'DPM', 'VS/m', 'DMG/Gold', 'KP', 'Level', 'CS/m']
        minutes = self.game.get_game_duration() / 60
        print(f"Game duration: {minutes:.2f} minutes")
        def extract_stats(player):
            return [
            player.get_kda(),
            player.get_total_damage() / minutes,
            player.get_vision_score() / minutes,
            player.get_damage_per_gold() / minutes,
            player.get_kill_participation(self.game.get_team_kills(player.get_team())),
            player.get_level(),
            player.get_cs() / minutes,
            ]

        stats_player_1 = extract_stats(position_players[0])
        stats_player_2 = extract_stats(position_players[1])

        # Normaliser les statistiques pour une comparaison équitable
        max_values = [max(s1, s2) for s1, s2 in zip(stats_player_1, stats_player_2)]
        normalized_player_1 = [s / m if m > 0 else 0 for s, m in zip(stats_player_1, max_values)]
        normalized_player_2 = [s / m if m > 0 else 0 for s, m in zip(stats_player_2, max_values)]

        angles = [n / float(len(stats_labels)) * 2 * 3.14159 for n in range(len(stats_labels))]
        angles.append(angles[0])

        # Ajouter le premier point à la fin pour fermer le graphique
        normalized_player_1.append(normalized_player_1[0])
        normalized_player_2.append(normalized_player_2[0])
        stats_labels.append(stats_labels[0])

        # Créer le graphique radar
        plt.figure(figsize=(8, 8))
        ax = plt.subplot(111, polar=True)
        ax.plot(angles, normalized_player_1, label=f"{position_players[0].get_name()} ({position_players[0].get_champion()})", color='blue')
        ax.fill(angles, normalized_player_1, color='blue', alpha=0.25)
        ax.plot(angles, normalized_player_2, label=f"{position_players[1].get_name()} ({position_players[1].get_champion()})", color='red')
        ax.fill(angles, normalized_player_2, color='red', alpha=0.25)

        # Ajouter les valeurs des statistiques sur le graphique
        for i, angle in enumerate(angles[:-1]):  # Exclure le dernier angle (répétition du premier)
            ax.text(angle, normalized_player_1[i] - 0.1, f"{stats_player_1[i]:.1f}", color='darkblue', ha='center', va='center', fontsize=8)
            ax.text(angle, normalized_player_2[i] - 0.1, f"{stats_player_2[i]:.1f}", color='darkred', ha='center', va='center', fontsize=8)

        # Configurer les étiquettes et le titre
        ax.set_yticks([])
        ax.set_xticks(angles)  # Ajouter un angle supplémentaire pour correspondre aux étiquettes
        ax.set_xticklabels(stats_labels)
        plt.title(f"Comparison for Position: {position}")
        plt.legend(loc='upper right', bbox_to_anchor=(1.3, 1.1))
        plt.tight_layout()
        plt.show()
        
    def _get_participant_names(self) -> List[str]:
        """Récupère les noms des participants."""
        return [f"{p.get_name()} ({p.get_champion()})" for p in self.participants]