from typing import List, Dict, Any

class HighlightDetector:
    def __init__(self):
        self.highlights = []
        self._kill_streaks = {}

    def detect_highlights(self, history: List[Dict[str, Any]], kill_log: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        self.highlights = []
        self._kill_streaks = {}

        self._detect_clutch_plays(history)
        self._detect_epic_kills(kill_log)
        self._detect_1v1_finals(history)

        return self.highlights

    def _detect_clutch_plays(self, history: List[Dict[str, Any]]):
        # A clutch play is when a ball survives with very low HP (e.g. < 5% or <= 5 absolute hp)
        # We can look for balls that hit low HP but remain alive for several ticks or kill an enemy
        for frame in history:
            tick = frame.get("tick", 0)
            for ball in frame.get("balls", []):
                # A clutch moment if HP is very low.
                hp = ball.get("hp", 0)
                max_hp = ball.get("max_hp", 100)
                # Let's say <= 5 HP or <= 5% HP
                if hp > 0 and (hp <= 5 or hp / max_hp <= 0.05):
                    # Check if we already have a highlight near this tick for this ball to avoid spam
                    already_highlighted = any(
                        h["type"] == "clutch_play" and h["ball_id"] == ball.get("id") and abs(h["tick"] - tick) < 50
                        for h in self.highlights
                    )
                    if not already_highlighted:
                        self.highlights.append({
                            "tick": tick,
                            "type": "clutch_play",
                            "ball_id": ball.get("id"),
                            "description": f"Ball {ball.get('id')} survives with {hp} HP!"
                        })

    def _detect_epic_kills(self, kill_log: List[Dict[str, Any]]):
        # Epic kills could be high kill streaks (e.g. double kill, triple kill)
        for log in kill_log:
            tick = log.get("tick", 0)
            killer_id = log.get("killer_id", 0)

            # Update streaks based on time
            # If the last kill was more than say 30 ticks ago, reset the streak
            if killer_id in self._kill_streaks:
                last_kill_tick = self._kill_streaks[killer_id]["last_tick"]
                streak = self._kill_streaks[killer_id]["streak"]
                if tick - last_kill_tick <= 30:
                    streak += 1
                else:
                    streak = 1
            else:
                streak = 1

            self._kill_streaks[killer_id] = {"streak": streak, "last_tick": tick}

            if streak == 2:
                self.highlights.append({
                    "tick": tick,
                    "type": "epic_kill",
                    "ball_id": killer_id,
                    "description": f"Double Kill by Ball {killer_id}!"
                })
            elif streak == 3:
                self.highlights.append({
                    "tick": tick,
                    "type": "epic_kill",
                    "ball_id": killer_id,
                    "description": f"Triple Kill by Ball {killer_id}!"
                })
            elif streak >= 4:
                self.highlights.append({
                    "tick": tick,
                    "type": "epic_kill",
                    "ball_id": killer_id,
                    "description": f"Rampage by Ball {killer_id}!"
                })

    def _detect_1v1_finals(self, history: List[Dict[str, Any]]):
        # Detect the moment when exactly 2 balls are left
        for frame in history:
            tick = frame.get("tick", 0)
            balls_alive = [b for b in frame.get("balls", []) if b.get("hp", 0) > 0 and b.get("type") != "spectator"]
            if len(balls_alive) == 2:
                # Add exactly one highlight for 1v1 finals
                if not any(h["type"] == "1v1_finals" for h in self.highlights):
                    b1, b2 = balls_alive[0], balls_alive[1]
                    self.highlights.append({
                        "tick": tick,
                        "type": "1v1_finals",
                        "description": f"1v1 Finals: Ball {b1.get('id')} vs Ball {b2.get('id')}"
                    })
                break
