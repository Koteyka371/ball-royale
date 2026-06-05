import math
from typing import Any, Dict, List


class Perception:
    """
    Scans the world to find nearby enemies, allies, boosters, traps.
    Calculates distances, threat levels, opportunity scores.
    """

    def __init__(self, ball: Any, world: Any):
        self.ball = ball
        self.world = world

    def scan(self) -> Dict[str, Any]:
        """
        Scans the environment within the ball's perception_radius.
        Returns a dictionary containing discovered entities and calculated scores.
        """
        data = {
            "enemies": [],
            "allies": [],
            "boosters": [],
            "traps": [],
            "distances": {},
            "danger_level": 0.0,
            "opportunity_level": 0.0,
        }

        # Default perception radius if not explicitly set on ball
        perception_radius = getattr(self.ball, "perception_radius", 300.0)

        if self.world and hasattr(self.world, "get_nearby_entities"):
            entities = self.world.get_nearby_entities(self.ball, perception_radius)

            data["enemies"] = entities.get("enemies", [])
            data["allies"] = entities.get("allies", [])
            data["boosters"] = entities.get("boosters", [])
            data["traps"] = entities.get("traps", [])

        # Calculate distances and normalize scores based on proximity

        # Danger level
        danger = 0.0
        for enemy in data["enemies"]:
            dist = self._calculate_distance(self.ball, enemy)
            if enemy:
                data["distances"][getattr(enemy, "id", id(enemy))] = dist
            if dist <= perception_radius:
                # Closer enemies contribute more to danger
                danger += max(0.0, 1.0 - (dist / perception_radius)) * 0.5

        # Traps also add to danger
        for trap in data["traps"]:
            dist = self._calculate_distance(self.ball, trap)
            if trap:
                data["distances"][getattr(trap, "id", id(trap))] = dist
            if dist <= perception_radius:
                danger += max(0.0, 1.0 - (dist / perception_radius)) * 0.8

        data["danger_level"] = min(1.0, danger)

        # Opportunity level
        opportunity = 0.0
        for booster in data["boosters"]:
            dist = self._calculate_distance(self.ball, booster)
            if booster:
                data["distances"][getattr(booster, "id", id(booster))] = dist
            if dist <= perception_radius:
                # Closer boosters contribute more to opportunity
                opportunity += max(0.0, 1.0 - (dist / perception_radius)) * 0.6

        for ally in data["allies"]:
            dist = self._calculate_distance(self.ball, ally)
            if ally:
                data["distances"][getattr(ally, "id", id(ally))] = dist
            if dist <= perception_radius:
                opportunity += max(0.0, 1.0 - (dist / perception_radius)) * 0.2

        data["opportunity_level"] = min(1.0, opportunity)

        return data

    def _calculate_distance(self, entity1: Any, entity2: Any) -> float:
        """Helper to calculate distance between two entities."""
        x1 = getattr(entity1, "x", 0.0)
        y1 = getattr(entity1, "y", 0.0)
        x2 = getattr(entity2, "x", 0.0)
        y2 = getattr(entity2, "y", 0.0)

        return math.sqrt((x2 - x1)**2 + (y2 - y1)**2)
