import json
import time
from typing import Dict, Any

class TournamentManager:
    TOURNAMENT_DURATION = 30 * 24 * 60 * 60  # 30 days in seconds

    def __init__(self, filename: str = "tournament.json", profile_manager=None):
        self.filename = filename
        self.profile_manager = profile_manager
        self.data = self.load()

    def load(self) -> Dict[str, Any]:
        try:
            with open(self.filename, 'r') as f:
                data = json.load(f)
                return data
        except (FileNotFoundError, json.JSONDecodeError):
            return {
                "tournament_start_time": time.time(),
                "current_tournament": 1,
                "player_scores": {}
            }

    def save(self):
        with open(self.filename, 'w') as f:
            json.dump(self.data, f, indent=4)

    def record_score(self, player_id: str, score: int):
        if "player_scores" not in self.data:
            self.data["player_scores"] = {}

        current_score = self.data["player_scores"].get(player_id, 0)
        self.data["player_scores"][player_id] = current_score + score
        self.save()

    def check_tournament_end(self):
        current_time = time.time()
        start_time = self.data.get("tournament_start_time", current_time)

        if current_time - start_time >= self.TOURNAMENT_DURATION:
            self.end_tournament()

    def end_tournament(self):
        tournament_num = self.data.get("current_tournament", 1)
        player_scores = self.data.get("player_scores", {})

        if player_scores:
            max_score = max(player_scores.values())
            top_players = [pid for pid, score in player_scores.items() if score == max_score]

            if "local_player" in top_players and self.profile_manager:
                self.profile_manager.add_cosmetic(f"Tournament {tournament_num} Champion Skin")
                self.profile_manager.add_status_effect(f"Aura of Tournament {tournament_num}")

        self.data["tournament_start_time"] = time.time()
        self.data["current_tournament"] = tournament_num + 1
        self.data["player_scores"] = {}
        self.save()
