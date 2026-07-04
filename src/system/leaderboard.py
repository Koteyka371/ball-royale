import json
import time

class LeaderboardManager:
    SEASON_DURATION = 30 * 24 * 60 * 60  # 30 days in seconds
    SEASON_THEMES = ["Genesis", "Inferno", "Frost", "Void", "Celestial", "Abyssal", "Ethereal", "Phantom", "Eclipse", "Radiance"]

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

    def record_loadout_win(self, loadout_code, is_win=True):
        if "loadouts" not in self.data:
            self.data["loadouts"] = {}

        if loadout_code not in self.data["loadouts"]:
            self.data["loadouts"][loadout_code] = {"uses": 0, "wins": 0}

        self.data["loadouts"][loadout_code]["uses"] += 1
        if is_win:
            self.data["loadouts"][loadout_code]["wins"] += 1

        self.save()

    def get_top_loadouts(self, limit=10):
        if "loadouts" not in self.data:
            return []

        loadouts = self.data["loadouts"]

        def sort_key(item):
            code, stats = item
            uses = stats.get("uses", 0)
            wins = stats.get("wins", 0)
            win_rate = (wins / uses) if uses > 0 else 0
            return (uses, win_rate)

        sorted_loadouts = sorted(loadouts.items(), key=sort_key, reverse=True)

        return [{"code": code, "uses": stats.get("uses", 0), "wins": stats.get("wins", 0)} for code, stats in sorted_loadouts[:limit]]

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

    def get_theme(self, season_num):
        index = (season_num - 1) % len(self.SEASON_THEMES)
        return self.SEASON_THEMES[index]

    def end_season(self):
        season_num = self.data.get("current_season", 1)
        players = self.data.get("players", {})

        if players:
            sorted_players = sorted(players.items(), key=lambda x: x[1], reverse=True)
            top_100 = [pid for pid, prestige in sorted_players[:100]]

            # If the local player is in the top 100, grant rewards
            if "local_player" in top_100 and self.profile_manager:
                theme = self.get_theme(season_num)
                self.profile_manager.add_cosmetic(f"Crown of {theme}")
                self.profile_manager.add_title(f"{theme} Champion")
                self.profile_manager.add_status_effect(f"Aura of {theme}")

            all_ranked_players = [p for p, _ in sorted_players]
            if "local_player" in all_ranked_players and self.profile_manager:
                rank = all_ranked_players.index("local_player") + 1
                theme = self.get_theme(season_num)
                badge_name = f"Season {season_num} Rank {rank} {theme} Badge"
                if hasattr(self.profile_manager, 'add_badge'):
                    self.profile_manager.add_badge(badge_name)

        # Reset for next season
        self.data["season_start_time"] = time.time()
        self.data["current_season"] = season_num + 1
        self.data["players"] = {}
        self.save()
