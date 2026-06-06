import math
from typing import Any, Dict

class Perception:
    """
    Perception system that scans the world for entities.
    Calculates distances, threat levels, and opportunity scores.
    """
    def __init__(self, ball: Any, world: Any):
        self.ball = ball
        self.world = world

    def scan(self) -> Dict[str, Any]:
        """
        Scans environment for entities (enemies, allies, boosters, traps).
        Calculates distances, danger and opportunity levels.
        """
        radius = getattr(self.ball, "perception_radius", 300.0)

        data: Dict[str, Any] = {
            "enemies": [],
            "allies": [],
            "boosters": [],
            "traps": [],
            "distances": {},
            "danger_level": 0.0,
            "opportunity_level": 0.0,
        }

        if not hasattr(self.world, "get_nearby_entities"):
            return data

        entities = self.world.get_nearby_entities(self.ball, radius)

        enemies = entities.get("enemies", [])
        allies = entities.get("allies", [])
        boosters = entities.get("boosters", [])
        traps = entities.get("traps", [])

        data["enemies"] = enemies
        data["allies"] = allies
        data["boosters"] = boosters
        data["traps"] = traps

        danger = 0.0
        opportunity = 0.0

        ball_pos = getattr(self.ball, "position", None)

        def calc_dist(entity: Any) -> float:
            if ball_pos is None:
                return -1.0
            entity_pos = getattr(entity, "position", None)
            if entity_pos is None:
                return -1.0
            if hasattr(ball_pos, "distance_to"):
                return ball_pos.distance_to(entity_pos)

            # fallback for simple test objects
            dx = getattr(entity_pos, "x", 0) - getattr(ball_pos, "x", 0)
            dy = getattr(entity_pos, "y", 0) - getattr(ball_pos, "y", 0)
            return math.sqrt(dx*dx + dy*dy)

        for e in enemies:
            dist = calc_dist(e)
            data["distances"][id(e)] = dist
            threat = 0.2
            if dist > 0:
                threat += 100.0 / max(dist, 1.0)
            danger += threat

        for t in traps:
            dist = calc_dist(t)
            data["distances"][id(t)] = dist
            threat = 0.5
            if dist > 0:
                threat += 50.0 / max(dist, 1.0)
            danger += threat

        for b in boosters:
            dist = calc_dist(b)
            data["distances"][id(b)] = dist
            opp = 0.3
            if dist > 0:
                opp += 100.0 / max(dist, 1.0)
            opportunity += opp

        for a in allies:
            dist = calc_dist(a)
            data["distances"][id(a)] = dist
            opportunity += 0.1

        data["danger_level"] = danger
        data["opportunity_level"] = opportunity

        return data
