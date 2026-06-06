import math
from typing import Any, Dict

class Perception:
    """
    Scans the world: finds nearby enemies, allies, boosters, traps.
    Calculates distances, threat levels, opportunity scores.
    Each ball has perception radius based on type.
    """

    def __init__(self, ball: Any, world: Any):
        self.ball = ball
        self.world = world

    def get_perception_radius(self) -> float:
        """Returns the perception radius for the ball."""
        if hasattr(self.ball, "perception_radius"):
            return float(self.ball.perception_radius)
        return 300.0  # default radius

    def scan(self) -> Dict[str, Any]:
        """
        Scans the environment and calculates threat and opportunity scores.
        """
        data = {
            "enemies": [],
            "allies": [],
            "boosters": [],
            "traps": [],
            "danger_level": 0.0,
            "opportunity_level": 0.0,
        }

        radius = self.get_perception_radius()

        if hasattr(self.world, "get_nearby_entities"):
            entities = self.world.get_nearby_entities(self.ball, radius)
            data["enemies"] = entities.get("enemies", [])
            data["allies"] = entities.get("allies", [])
            data["boosters"] = entities.get("boosters", [])
            data["traps"] = entities.get("traps", [])

        # In testing we can also just provide it via the ball if needed,
        # but the standard way is from the world.

        enemies = data.get("enemies", [])
        boosters = data.get("boosters", [])
        allies = data.get("allies", [])
        traps = data.get("traps", [])

        # Calculate distances if possible
        def calc_distance(entity):
            if hasattr(self.ball, "position") and hasattr(entity, "position"):
                try:
                    # simplistic distance calc assuming .position is an object with x, y
                    # or dict or something. This assumes standard Godot Vector2-like access in python
                    dx = getattr(self.ball.position, "x", 0) - getattr(entity.position, "x", 0)
                    dy = getattr(self.ball.position, "y", 0) - getattr(entity.position, "y", 0)
                    return math.sqrt(dx*dx + dy*dy)
                except Exception:
                    pass
            return radius # default max distance

        # Advanced calculation for danger and opportunity
        danger_score = 0.0
        for e in enemies:
            dist = calc_distance(e)
            # Closer enemies are more dangerous
            danger_score += 1.0 * (1.0 - min(dist / radius, 1.0))

        for t in traps:
            dist = calc_distance(t)
            # Closer traps are more dangerous
            danger_score += 1.5 * (1.0 - min(dist / radius, 1.0))

        opp_score = 0.0
        for b in boosters:
            dist = calc_distance(b)
            # Closer boosters are better opportunities
            opp_score += 1.5 * (1.0 - min(dist / radius, 1.0))

        for a in allies:
            dist = calc_distance(a)
            # Closer allies are good
            opp_score += 0.5 * (1.0 - min(dist / radius, 1.0))

        # We keep the old simplistic calc fallback if we can't do distance based
        if danger_score == 0 and len(enemies) > 0:
            danger_score = len(enemies) * 0.2

        if opp_score == 0 and (len(boosters) > 0 or len(allies) > 0):
            opp_score = len(boosters) * 0.3 + len(allies) * 0.1

        data["danger_level"] = danger_score
        data["opportunity_level"] = opp_score

        return data
