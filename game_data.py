import json
from typing import List, Optional
from participant_data import ParticipantData

class GameData:
    """Class to manage game data."""
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.data = self._load_data()
        self.participants = self._load_participants()

    def _load_data(self) -> Optional[dict]:
        """Load JSON data from file."""
        try:
            with open(self.file_path, 'r') as file:
                return json.load(file)
        except FileNotFoundError:
            print(f"File not found: {self.file_path}")
        except json.JSONDecodeError:
            print(f"Error decoding JSON from file: {self.file_path}")
        return None

    def _load_participants(self) -> List[ParticipantData]:
        """Load participant data."""
        if self.data and "participants" in self.data:
            return [ParticipantData(p) for p in self.data["participants"]]
        return []

    def get_participant(self, index: int) -> Optional[ParticipantData]:
        """Get a participant by index."""
        if 0 <= index < len(self.participants):
            return self.participants[index]
        print(f"Index {index} is out of range.")
        return None

    def get_game_duration(self) -> int:
        """Get game duration in seconds."""
        return int(self.data.get("gameDuration", 0)) // 1000 if self.data else 0
    
    def get_game_duration_formatted(self) -> str:
        """Get formatted game duration."""
        duration = self.get_game_duration()
        minutes, seconds = divmod(duration, 60)
        return f"{minutes}:{seconds}"

    def get_version(self) -> str:
        """Get game version."""
        return self.data.get("gameVersion", "Unknown")

    def get_team_damage(self, team: str) -> int:
        """Get total damage for a team."""
        return sum(p.get_total_damage() for p in self.participants if p.get_team() == team)

    def get_all_participants(self) -> List[ParticipantData]:
        """Get all participants."""
        return self.participants
    
    def get_team_kills(self, team: str) -> int:
        """Get total kills for a team."""
        return sum(p.get_kills() for p in self.participants if p.get_team() == team)
