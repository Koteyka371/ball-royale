import math
from typing import Any, Dict, List

class Perception:
    """
    Perception system for balls.
    Scans the world to find nearby enemies, allies, boosters, and traps.
    Calculates distances, threat levels, and opportunity scores.
    """
    def __init__(self, ball: Any, world: Any):
        self.ball = ball
        self.world = world

    def scan(self) -> Dict[str, Any]:
        radius = getattr(self.ball, 'perception_radius', 300.0)

        data = {
            "enemies": [],
            "allies": [],
            "boosters": [],
            "traps": [],
            "danger_level": 0.0,
            "opportunity_level": 0.0,
        }

        if hasattr(self.world, "get_nearby_entities"):
            entities = self.world.get_nearby_entities(self.ball, radius)
            data["enemies"] = entities.get("enemies", [])
            data["allies"] = entities.get("allies", [])
            data["boosters"] = entities.get("boosters", [])
            data["traps"] = entities.get("traps", [])

        # Calculate distances and threat/opportunity levels
        danger_level = 0.0
        opportunity_level = 0.0

        bx = getattr(self.ball, 'x', 0)
        by = getattr(self.ball, 'y', 0)

        for enemy in data["enemies"]:
            ex = getattr(enemy, 'x', 0)
            ey = getattr(enemy, 'y', 0)
            dist = math.sqrt((bx - ex)**2 + (by - ey)**2)
            # Closer enemies pose more threat. Scale threat based on radius
            dist_factor = max(0, 1.0 - (dist / radius)) if radius > 0 else 0
            base_threat = getattr(enemy, 'damage', 10.0) / 100.0
            danger_level += base_threat * dist_factor + 0.1

        for trap in data["traps"]:
            tx = getattr(trap, 'x', 0)
            ty = getattr(trap, 'y', 0)
            dist = math.sqrt((bx - tx)**2 + (by - ty)**2)
            dist_factor = max(0, 1.0 - (dist / radius)) if radius > 0 else 0
            danger_level += 0.5 * dist_factor

        for booster in data["boosters"]:
            boox = getattr(booster, 'x', 0)
            booy = getattr(booster, 'y', 0)
            dist = math.sqrt((bx - boox)**2 + (by - booy)**2)
            dist_factor = max(0, 1.0 - (dist / radius)) if radius > 0 else 0
            opportunity_level += 0.3 * dist_factor + 0.1

        for ally in data["allies"]:
            ax = getattr(ally, 'x', 0)
            ay = getattr(ally, 'y', 0)
            dist = math.sqrt((bx - ax)**2 + (by - ay)**2)
            dist_factor = max(0, 1.0 - (dist / radius)) if radius > 0 else 0
            opportunity_level += 0.1 * dist_factor

        data["danger_level"] = danger_level
        data["opportunity_level"] = opportunity_level

        return data
