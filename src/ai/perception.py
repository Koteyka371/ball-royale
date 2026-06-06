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
        """
        Scans the environment within the ball's perception radius.
        Returns a dictionary with parsed data.
        """
        data = {
            "enemies": [],
            "allies": [],
            "boosters": [],
            "traps": [],
            "danger_level": 0.0,
            "opportunity_level": 0.0,
        }

        if not self.world or not hasattr(self.world, "get_nearby_entities"):
            return data

        radius = getattr(self.ball, "perception_radius", 300.0)
        entities = self.world.get_nearby_entities(self.ball, radius)

        # Parse entities and calculate distances
        data["enemies"] = self._process_entities(entities.get("enemies", []), is_threat=True)
        data["allies"] = self._process_entities(entities.get("allies", []), is_threat=False)
        data["boosters"] = self._process_entities(entities.get("boosters", []), is_threat=False)
        data["traps"] = self._process_entities(entities.get("traps", []), is_threat=True)

        # Calculate danger and opportunity levels
        data["danger_level"] = self._calculate_danger(data["enemies"], data["traps"])
        data["opportunity_level"] = self._calculate_opportunity(data["boosters"], data["allies"])

        return data

    def _process_entities(self, entities: List[Any], is_threat: bool) -> List[Dict[str, Any]]:
        """Processes a list of entities, calculating distances and returning enriched dicts."""
        processed = []
        for entity in entities:
            # Handle dictionaries (like from simulate_battle.py logs) or objects
            if isinstance(entity, dict):
                ex, ey = entity.get("x", 0), entity.get("y", 0)
            else:
                ex, ey = getattr(entity, "x", 0), getattr(entity, "y", 0)

            bx, by = getattr(self.ball, "x", 0), getattr(self.ball, "y", 0)

            dx = ex - bx
            dy = ey - by
            dist = math.sqrt(dx*dx + dy*dy)

            processed.append({
                "entity": entity,
                "distance": dist,
                "direction": (dx, dy)
            })

        # Sort by distance (closest first)
        return sorted(processed, key=lambda x: x["distance"])

    def _calculate_danger(self, enemies: List[Dict[str, Any]], traps: List[Dict[str, Any]]) -> float:
        """Calculates danger level based on nearby threats."""
        danger = 0.0

        # Enemies are dangerous, especially if close
        for e in enemies:
            dist = max(e["distance"], 1.0) # Prevent div by 0
            # closer = more danger (e.g. 0.5 at 100 dist, 1.0 at 50 dist)
            danger += min(1.0, 50.0 / dist)

        # Traps are very dangerous if very close
        for t in traps:
            dist = max(t["distance"], 1.0)
            if dist < 50.0:
                danger += min(1.0, 50.0 / dist)

        return danger

    def _calculate_opportunity(self, boosters: List[Dict[str, Any]], allies: List[Dict[str, Any]]) -> float:
        """Calculates opportunity level based on nearby resources and support."""
        opportunity = 0.0

        # Boosters are good opportunities, especially if close
        for b in boosters:
            dist = max(b["distance"], 1.0)
            opportunity += min(1.0, 100.0 / dist)

        # Allies provide small opportunity/safety
        opportunity += len(allies) * 0.1

        return opportunity
