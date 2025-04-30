class ParticipantData:
    """Classe pour gérer les données d'un participant."""
    def __init__(self, data: dict):
        self.data = data

    def get_name(self) -> str:
        """Retourne le nom du joueur."""
        return self.data.get("riotIdGameName", "Unknown")

    def get_total_damage(self) -> int:
        """Retourne les dégâts totaux infligés aux champions."""
        return int(self.data.get("totalDamageDealtToChampions", 0))

    def get_team(self) -> str:
        """Retourne l'équipe du joueur (100 ou 200)."""
        return self.data.get("team", "Unknown")

    def get_position(self) -> str:
        """Retourne la position du joueur (TOP, JUNGLE, etc.)."""
        return self.data.get("individualPosition", "Unknown")

    def get_kills(self) -> int:
        """Retourne le nombre de kills."""
        return int(self.data.get("championsKilled", 0))

    def get_deaths(self) -> int:
        """Retourne le nombre de morts."""
        return int(self.data.get("numDeaths", 0))

    def get_assists(self) -> int:
        """Retourne le nombre d'assists."""
        return int(self.data.get("assists", 0))
    
    def get_champion(self) -> str:
        """Retourne le nom du champion joué."""
        return self.data.get("skin", "Unknown")
    
    def get_cs(self) -> int:
        """Retourne le nombre de sbires tués (CS)."""
        return int(self.data.get("minionsKilled", 0)) + int(self.data.get("neutralMinionsKilled", 0))

    def get_cc_time(self) -> int:
        """Retourne le temps de contrôle de foule infligé aux autres (en secondes)."""
        return int(self.data.get("totalTimeCrowdControlDealt", 0))

    def get_vision_score(self) -> int:
        """Retourne le score de vision."""
        return int(self.data.get("visionScore", 0))

    def get_damage_taken(self) -> int:
        """Retourne les dégâts subis."""
        return int(self.data.get("totalDamageTaken", 0))

    def get_total_heal(self) -> int:
        """Retourne le total des soins effectués."""
        return int(self.data.get("totalHeal", 0))

    def get_healing_on_teammates(self) -> int:
        """Retourne le total des soins effectués sur les alliés."""
        return int(self.data.get("totalHealOnTeammates", 0))
    
    def get_gold_spent(self) -> int:
        """Retourne le total d'or dépensé."""
        return int(self.data.get("goldSpent", 0))

    def get_damage_per_gold(self) -> float:
        """Retourne les dégâts infligés par or dépensé."""
        gold_spent = self.get_gold_spent()
        return self.get_total_damage() / gold_spent if gold_spent > 0 else 0.0
    
    def get_level(self) -> int:
        """Retourne le niveau du joueur."""
        return int(self.data.get("level", 0))
    
    def get_kda(self) -> float:
        """Retourne le KDA (Kills + Assists) / Deaths."""
        deaths = self.get_deaths()
        return (self.get_kills() + self.get_assists()) / deaths if deaths > 0 else self.get_kills() + self.get_assists()
    
    def get_kill_participation(self, team_kills: int) -> float:
        """Retourne la participation aux kills (Kill Participation)."""
        if team_kills > 0:
            return (self.get_kills() + self.get_assists()) / team_kills
        return 0.0