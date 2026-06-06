import math
from typing import Any, Dict

class Perception:
    """
    Perception system for balls.
    Scans the world, finds nearby entities, and calculates threat/opportunity scores.
    """

    def __init__(self, ball: Any, world: Any):
        self.ball = ball
        self.world = world

    def scan(self) -> Dict[str, Any]:
        """
        Scans environment for entities (enemies, allies, boosters).
        Calculates danger and opportunity levels based on distances and stats.
        """
        radius = getattr(self.ball, "PERCEPTION_RADIUS", 300.0)

        data: Dict[str, Any] = {
            "enemies": [],
            "allies": [],
            "boosters": [],
            "traps": [],
            "danger_level": 0.0,
            "opportunity_level": 0.0,
            "closest_enemy_dist": float('inf'),
            "closest_ally_dist": float('inf'),
            "closest_booster_dist": float('inf'),
            "closest_trap_dist": float('inf'),
        }

        if hasattr(self.world, "get_nearby_entities"):
            entities = self.world.get_nearby_entities(self.ball, radius)
            data["enemies"] = entities.get("enemies", [])
            data["allies"] = entities.get("allies", [])
            data["boosters"] = entities.get("boosters", [])
            data["traps"] = entities.get("traps", [])

        # Process enemies to calculate danger
        danger = 0.0
        enemies = data.get("enemies", [])
        if isinstance(enemies, list):
            for enemy in enemies:
                dist = self._calculate_distance(self.ball, enemy)
                data["closest_enemy_dist"] = min(data["closest_enemy_dist"], dist)

                # Base threat depends on distance
                threat = 0.2
                if dist < radius:
                    threat += 0.2 * (1.0 - (dist / radius))

                # Threat depends on enemy damage potential
                damage = getattr(enemy, "DAMAGE", 10.0)
                threat *= (damage / 10.0)

                danger += threat
        data["danger_level"] = danger

        # Process boosters to calculate opportunity
        opportunity = 0.0
        boosters = data.get("boosters", [])
        if isinstance(boosters, list):
            for booster in boosters:
                # If booster is just a number (mock), handle it gracefully
                if isinstance(booster, (int, float)):
                    opportunity += 0.3
                    continue

                dist = self._calculate_distance(self.ball, booster)
                data["closest_booster_dist"] = min(data["closest_booster_dist"], dist)

                opp = 0.3
                if dist < radius:
                    opp += 0.2 * (1.0 - (dist / radius))
                opportunity += opp

        # Process allies to calculate opportunity
        allies = data.get("allies", [])
        if isinstance(allies, list):
            for ally in allies:
                dist = self._calculate_distance(self.ball, ally)
                data["closest_ally_dist"] = min(data["closest_ally_dist"], dist)

                opp = 0.1
                if dist < radius:
                    opp += 0.1 * (1.0 - (dist / radius))
                opportunity += opp

        data["opportunity_level"] = opportunity

        return data

    def _calculate_distance(self, entity1: Any, entity2: Any) -> float:
        """Calculates distance between two entities using x and y if available."""
        if hasattr(entity1, "x") and hasattr(entity1, "y") and hasattr(entity2, "x") and hasattr(entity2, "y"):
            dx = entity1.x - entity2.x
            dy = entity1.y - entity2.y
            return math.sqrt(dx*dx + dy*dy)
        return float('inf') # Fallback if no position
