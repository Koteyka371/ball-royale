from typing import List, Dict, Any
from ui.kill_feed import KillFeed

class BattleCommentator:
    """
    Generates dynamic text commentary based on the simulation kill_log and stats.
    """
    def __init__(self):
        self.kill_feed = KillFeed()

    def generate_commentary(self, kill_log: List[Dict[str, Any]], stats: Dict[str, Any]) -> List[str]:
        lines: List[str] = []
        if not kill_log:
            return lines

        self.kill_feed.update(kill_log)

        streaks: Dict[int, int] = {}

        for i, event in enumerate(kill_log):
            if event.get("type") == "weather_change":
                weather = event.get("weather", "clear")
                lines.append(f"[WEATHER] The weather has shifted to {weather.upper()}! Adapt or perish!")
                continue
            elif event.get("type") == "crowd_cheer":
                lines.append(f"[CROWD] {event.get('message')}")
                continue
            elif event.get("type") == "crowd_throw":
                lines.append(f"[CROWD] {event.get('message')}")
                continue
            elif event.get("type") in ["audio_event", "weather_warning", "spawn_booster"]:
                continue

            tick = event.get("tick", 0)
            killer_id = event.get("killer_id", 0)
            killer_type = event.get("killer_type", "unknown")
            victim_id = event.get("victim_id", 0)
            victim_type = event.get("victim_type", "unknown")

            # Reset streaks for victim
            streaks[victim_id] = 0

            # Increment streak for killer
            streaks[killer_id] = streaks.get(killer_id, 0) + 1
            streak = streaks[killer_id]

            # First blood
            if i == 0:
                lines.append(f"[FIRST BLOOD] The {killer_type} #{killer_id} drew first blood by eliminating {victim_type} #{victim_id}!")
            else:
                lines.append(f"[Tick {tick}] The {killer_type} #{killer_id} brutally eliminated {victim_type} #{victim_id}!")

            # Streak messages
            if streak == 2:
                lines.append(f"[DOUBLE KILL] {killer_type} #{killer_id} is heating up!")
            elif streak == 3:
                lines.append(f"[TRIPLE KILL] {killer_type} #{killer_id} is unstoppable!")
            elif streak >= 4:
                lines.append(f"[RAMPAGE] {killer_type} #{killer_id} is on a rampage!")

        # Final summary
        winner = stats.get("winner")
        if winner:
            lines.append(f"[VICTORY] The {winner} type emerged victorious!")
        else:
            lines.append("[DRAW] Nobody survived the carnage!")

        return lines
