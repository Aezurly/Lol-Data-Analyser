class ParticipantData:
    """Class to manage participant data."""
    def __init__(self, data: dict):
        self.data = data

    def get_name(self) -> str:
        """Returns player name."""
        return self.data.get("riotIdGameName", "Unknown")

    def get_total_damage(self) -> int:
        """Returns total damage dealt to champions."""
        return int(self.data.get("totalDamageDealtToChampions", 0))

    def get_team(self) -> str:
        """Returns player's team."""
        return self.data.get("team", "Unknown")

    def get_position(self) -> str:
        """Returns player's position."""
        return self.data.get("individualPosition", "Unknown")

    def get_kills(self) -> int:
        """Returns number of kills."""
        return int(self.data.get("championsKilled", 0))

    def get_deaths(self) -> int:
        """Returns number of deaths."""
        return int(self.data.get("numDeaths", 0))

    def get_assists(self) -> int:
        """Returns number of assists."""
        return int(self.data.get("assists", 0))
    
    def get_champion(self) -> str:
        """Returns champion name."""
        return self.data.get("skin", "Unknown")
    
    def get_cs(self) -> int:
        """Returns total CS."""
        return int(self.data.get("minionsKilled", 0)) + int(self.data.get("neutralMinionsKilled", 0))

    def get_cc_time(self) -> int:
        """Returns crowd control time."""
        return int(self.data.get("totalTimeCrowdControlDealt", 0))

    def get_vision_score(self) -> int:
        """Returns vision score."""
        return int(self.data.get("visionScore", 0))

    def get_damage_taken(self) -> int:
        """Returns damage taken."""
        return int(self.data.get("totalDamageTaken", 0))

    def get_total_heal(self) -> int:
        """Returns total healing done."""
        return int(self.data.get("totalHeal", 0))

    def get_healing_on_teammates(self) -> int:
        """Returns healing done on teammates."""
        return int(self.data.get("totalHealOnTeammates", 0))
    
    def get_gold_spent(self) -> int:
        """Returns total gold spent."""
        return int(self.data.get("goldSpent", 0))

    def get_damage_per_gold(self) -> float:
        """Returns damage per gold spent."""
        gold_spent = self.get_gold_spent()
        return self.get_total_damage() / gold_spent if gold_spent > 0 else 0.0
    
    def get_level(self) -> int:
        """Returns player's level."""
        return int(self.data.get("level", 0))
    
    def get_kda(self) -> float:
        """Returns KDA."""
        deaths = self.get_deaths()
        return (self.get_kills() + self.get_assists()) / deaths if deaths > 0 else self.get_kills() + self.get_assists()
    
    def get_kill_participation(self, team_kills: int) -> float:
        """Returns kill participation."""
        if team_kills > 0:
            return (self.get_kills() + self.get_assists()) / team_kills
        return 0.0