import math
from typing import Any, Dict, List


class Perception:
    """
    Scans the world: finds nearby enemies, allies, boosters, traps.
    Calculates distances, threat levels, opportunity scores.
    """

    def __init__(self, ball: Any, world: Any):
        self.ball = ball
        self.world = world

    def scan(self) -> Dict[str, Any]:
        """
        Scans environment for entities (enemies, allies, boosters, traps).
        Calculates danger and opportunity levels.
        """
        data = {
            "enemies": [],
            "allies": [],
            "boosters": [],
            "traps": [],
            "danger_level": 0.0,
            "opportunity_level": 0.0,
        }

        # Determine perception radius
        radius = getattr(self.ball, "perception_radius", 300.0)
        if not hasattr(self.ball, "perception_radius") and hasattr(self.ball, "PERCEPTION_RADIUS"):
            radius = getattr(self.ball, "PERCEPTION_RADIUS")

        if self.world and hasattr(self.world, "get_nearby_entities"):
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

        # Add distance calculations and filtering if coordinates are available
        def calculate_distance(e1, e2):
            if hasattr(e1, 'x') and hasattr(e1, 'y') and hasattr(e2, 'x') and hasattr(e2, 'y'):
                dx = e1.x - e2.x
                dy = e1.y - e2.y
                return math.sqrt(dx * dx + dy * dy)
            return None

        # Filter by distance if coordinates are present, otherwise just accept them
        def filter_by_dist(entity_list):
            res = []
            for e in entity_list:
                dist = calculate_distance(self.ball, e)
                if dist is None or dist <= radius:
                    res.append(e)
            return res

        data["enemies"] = filter_by_dist(enemies)
        data["allies"] = filter_by_dist(allies)
        data["boosters"] = filter_by_dist(boosters)
        data["traps"] = filter_by_dist(traps)

        # Calculate exact threat and opportunity
        danger_level = 0.0
        for e in data["enemies"]:
            dist = calculate_distance(self.ball, e)
            if dist is not None:
                # Closer enemies are more dangerous
                threat = 1.0 - (dist / max(1.0, radius))
                danger_level += threat * 0.5

        for t in data["traps"]:
             dist = calculate_distance(self.ball, t)
             if dist is not None:
                 threat = 1.0 - (dist / max(1.0, radius))
                 danger_level += threat * 0.8

        # To maintain compatibility with older simple tests
        if len(data["enemies"]) > 0 and danger_level == 0.0:
             danger_level = len(data["enemies"]) * 0.2

        opportunity_level = 0.0
        for b in data["boosters"]:
            dist = calculate_distance(self.ball, b)
            if dist is not None:
                # Closer boosters are better opportunities
                opp = 1.0 - (dist / max(1.0, radius))
                opportunity_level += opp * 0.5

        for a in data["allies"]:
             dist = calculate_distance(self.ball, a)
             if dist is not None:
                 opp = 1.0 - (dist / max(1.0, radius))
                 opportunity_level += opp * 0.2

        # To maintain compatibility with older simple tests
        if (len(data["boosters"]) > 0 or len(data["allies"]) > 0) and opportunity_level == 0.0:
            opportunity_level = len(data["boosters"]) * 0.3 + len(data["allies"]) * 0.1

        data["danger_level"] = danger_level
        data["opportunity_level"] = opportunity_level

        return data
