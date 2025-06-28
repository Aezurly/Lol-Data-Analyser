# MODEL: Participant data representation and business logic for player statistics
from constants import UNKNOWN_VALUE

class ParticipantData:
    """Class to manage participant data."""
    def __init__(self, data: dict):
        self.data = data

    def _get_field(self, field_name: str, alt_field_name: str = None) -> str:
        """Get field value with fallback for different naming conventions."""
        # Try main field name first (SCREAMING_SNAKE_CASE)
        if field_name in self.data:
            return self.data[field_name]
        # Try alternative field name (camelCase)
        if alt_field_name and alt_field_name in self.data:
            return self.data[alt_field_name]
        # Return default
        return "0"

    def get_name(self) -> str:
        """Returns player name."""
        return self._get_field("RIOT_ID_GAME_NAME", "riotIdGameName") or UNKNOWN_VALUE

    def get_total_damage(self) -> int:
        """Returns total damage dealt to champions."""
        return int(self._get_field("TOTAL_DAMAGE_DEALT_TO_CHAMPIONS", "totalDamageDealtToChampions"))

    def get_team(self) -> str:
        """Returns player's team."""
        return self._get_field("TEAM", "team") or UNKNOWN_VALUE

    def get_position(self) -> str:
        """Returns player's position."""
        return self._get_field("INDIVIDUAL_POSITION", "individualPosition") or UNKNOWN_VALUE

    def get_kills(self) -> int:
        """Returns number of kills."""
        return int(self._get_field("CHAMPIONS_KILLED", "championsKilled"))

    def get_deaths(self) -> int:
        """Returns number of deaths."""
        return int(self._get_field("NUM_DEATHS", "numDeaths"))

    def get_assists(self) -> int:
        """Returns number of assists."""
        return int(self._get_field("ASSISTS", "assists"))
    
    def get_champion(self) -> str:
        """Returns champion name."""
        return self._get_field("SKIN", "skin") or UNKNOWN_VALUE
    
    def get_cs(self) -> int:
        """Returns total CS."""
        minions = int(self._get_field("MINIONS_KILLED", "minionsKilled"))
        neutral = int(self._get_field("NEUTRAL_MINIONS_KILLED", "neutralMinionsKilled"))
        return minions + neutral

    def get_cc_time(self) -> int:
        """Returns crowd control time."""
        return int(self._get_field("TOTAL_TIME_CROWD_CONTROL_DEALT", "totalTimeCrowdControlDealt"))

    def get_vision_score(self) -> int:
        """Returns vision score."""
        return int(self._get_field("VISION_SCORE", "visionScore"))

    def get_damage_taken(self) -> int:
        """Returns damage taken."""
        return int(self._get_field("TOTAL_DAMAGE_TAKEN", "totalDamageTaken"))

    def get_total_heal(self) -> int:
        """Returns total healing done."""
        return int(self._get_field("TOTAL_HEAL", "totalHeal"))

    def get_healing_on_teammates(self) -> int:
        """Returns healing done on teammates."""
        return int(self._get_field("TOTAL_HEALING_ON_TEAMMATES", "totalHealingOnTeammates"))
    def get_gold_spent(self) -> int:
        """Returns total gold spent."""
        return int(self._get_field("GOLD_SPENT", "goldSpent"))
    
    def get_gold_earned(self) -> int:
        """Returns total gold earned."""
        return int(self._get_field("GOLD_EARNED", "goldEarned"))

    def get_damage_per_gold(self) -> float:
        """Returns damage per gold spent."""
        gold_spent = self.get_gold_spent()
        return self.get_total_damage() / gold_spent if gold_spent > 0 else 0.0
    
    def get_level(self) -> int:
        """Returns player's level."""
        return int(self._get_field("LEVEL", "level"))
    
    def get_kda(self) -> float:
        """Returns KDA."""
        deaths = self.get_deaths()
        return (self.get_kills() + self.get_assists()) / deaths if deaths > 0 else self.get_kills() + self.get_assists()
    
    def get_win(self) -> bool:
        """Returns whether the player won the game."""
        win_value = self._get_field("WIN", "win")
        return win_value in ["Win", "1", 1, True]
    
    def get_kill_participation(self, team_kills: int) -> float:
        """Returns kill participation."""
        if team_kills > 0:
            return (self.get_kills() + self.get_assists()) / team_kills
        return 0.0