from typing import Dict, Any, List

class StatsOverlay:
    """
    Tracks and formats battle statistics for display on screen.
    """
    def __init__(self):
        self.stats: Dict[str, Any] = {
            "ticks": 0,
            "battle_duration": 0.0,
            "total_kills": 0,
            "survivors": 0,
            "winner": None,
            "longest_killstreak": 0,
            "avg_hp_at_end": 0.0,
            "ball_types_alive": {},
        }

    def update(self, current_stats: Dict[str, Any]):
        """Updates the internal stats with new values."""
        for key in self.stats:
            if key in current_stats:
                self.stats[key] = current_stats[key]

    def get_display_lines(self) -> List[str]:
        """Formats the stats into a list of strings for display."""
        lines = [
            "=== BATTLE STATS ===",
            f"Time: {self.stats['battle_duration']}s (Ticks: {self.stats['ticks']})",
            f"Survivors: {self.stats['survivors']}  |  Kills: {self.stats['total_kills']}",
        ]

        if self.stats['winner']:
            lines.append(f"Winner: {str(self.stats['winner']).upper()}")
        else:
            lines.append("Winner: None")

        lines.append(f"Highest Killstreak: {self.stats['longest_killstreak']}")

        if self.stats['avg_hp_at_end'] > 0:
            lines.append(f"Avg End HP: {self.stats['avg_hp_at_end']}")

        if self.stats['ball_types_alive']:
            types_str = ", ".join(f"{k}: {v}" for k, v in self.stats['ball_types_alive'].items())
            lines.append(f"Alive Types: {types_str}")

        return lines
