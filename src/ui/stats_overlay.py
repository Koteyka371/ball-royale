from typing import Dict, Any

class StatsOverlay:
    def __init__(self):
        self.stats = {
            "alive": 0,
            "total_kills": 0,
            "top_killstreak": 0,
            "fps": 60,
            "tick": 0
        }
        self.visible = True

    def update(self, battle_stats: Dict[str, Any], current_tick: int, fps: int = 60):
        self.stats["tick"] = current_tick
        self.stats["fps"] = fps
        self.stats["total_kills"] = battle_stats.get("total_kills", 0)
        self.stats["top_killstreak"] = battle_stats.get("longest_killstreak", 0)

        if "survivors" in battle_stats:
            self.stats["alive"] = battle_stats["survivors"]
        elif "ball_types_alive" in battle_stats:
            alive_counts = battle_stats["ball_types_alive"]
            if isinstance(alive_counts, dict):
                self.stats["alive"] = sum(alive_counts.values())
            else:
                self.stats["alive"] = 0
        else:
            self.stats["alive"] = 0

    def get_text_display(self) -> str:
        if not self.visible:
            return ""
        lines = [
            "=== STATS ===",
            f"Tick: {self.stats['tick']}",
            f"FPS: {self.stats['fps']}",
            f"Alive: {self.stats['alive']}",
            f"Total Kills: {self.stats['total_kills']}",
            f"Top Killstreak: {self.stats['top_killstreak']}",
            "============="
        ]
        return "\n".join(lines)

    def toggle_visibility(self):
        self.visible = not self.visible
