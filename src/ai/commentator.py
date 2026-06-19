from typing import List, Dict, Any
from ui.kill_feed import KillFeed
from ui.stats_overlay import StatsOverlay


class BattleCommentator:
    """
    Generates dynamic text commentary based on the simulation kill_log and stats.
    """
    def __init__(self):
        self.kill_feed = KillFeed()
        self.stats_overlay = StatsOverlay()

    def generate_commentary(self, kill_log: List[Dict[str, Any]], stats: Dict[str, Any]) -> List[str]:
        lines: List[str] = []
        current_tick = kill_log[-1]["tick"] if kill_log else stats.get("ticks", 0)
        self.stats_overlay.update(stats, current_tick)

        overlay_text = self.stats_overlay.get_text_display()
        if overlay_text:
            lines.append(overlay_text)

        if not kill_log:
            return lines

        self.kill_feed.update(kill_log)

        streaks: Dict[int, int] = {}

        for i, event in enumerate(kill_log):
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
