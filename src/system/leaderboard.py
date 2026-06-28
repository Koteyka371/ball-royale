import json
import time

class LeaderboardManager:
    SEASON_DURATION = 30 * 24 * 60 * 60  # 30 days in seconds

    def __init__(self, filename="leaderboard.json", profile_manager=None):
        self.filename = filename
        self.profile_manager = profile_manager
        self.data = self.load()

    def load(self):
        try:
            with open(self.filename, 'r') as f:
                data = json.load(f)
                return data
        except (FileNotFoundError, json.JSONDecodeError):
            return {
                "season_start_time": time.time(),
                "current_season": 1,
                "players": {}
            }

    def save(self):
        with open(self.filename, 'w') as f:
            json.dump(self.data, f, indent=4)

    def update_prestige(self, player_id, prestige_level):
        if "players" not in self.data:
            self.data["players"] = {}

        # Only update if the new prestige is higher
        if self.data["players"].get(player_id, 0) < prestige_level:
            self.data["players"][player_id] = prestige_level
            self.save()

    def check_season(self):
        current_time = time.time()
        start_time = self.data.get("season_start_time", current_time)

        if current_time - start_time >= self.SEASON_DURATION:
            self.end_season()

    def end_season(self):
        season_num = self.data.get("current_season", 1)
        players = self.data.get("players", {})

        if players:
            max_prestige = max(players.values())
            top_players = [pid for pid, prestige in players.items() if prestige == max_prestige]

            # If the local player is one of the top players, grant rewards
            if "local_player" in top_players and self.profile_manager:
                self.profile_manager.add_cosmetic(f"Crown of Season {season_num}")
                self.profile_manager.add_title(f"Season {season_num} Champion")

        # Reset for next season
        self.data["season_start_time"] = time.time()
        self.data["current_season"] = season_num + 1
        self.data["players"] = {}
        self.save()
