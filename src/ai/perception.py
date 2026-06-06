import math
from typing import Any, Dict, List

class Perception:
    """
    Perception class that scans the world for entities (enemies, allies, boosters, traps).
    Calculates distances, threat levels, and opportunity scores.
    """

    def __init__(self, ball: Any, world: Any):
        self.ball = ball
        self.world = world

    def scan(self) -> Dict[str, Any]:
        """
        Scans environment and returns perception data.
        """
        data = {
            "enemies": [],
            "allies": [],
            "boosters": [],
            "traps": [],
            "danger_level": 0.0,
            "opportunity_level": 0.0,
            "nearest_enemy": None,
            "nearest_booster": None,
            "nearest_ally": None,
        }

        radius = getattr(self.ball, "perception_radius", 300.0)

        if hasattr(self.world, "get_nearby_entities"):
            entities = self.world.get_nearby_entities(self.ball, radius)
            # Basic fetching from world
            data["enemies"] = entities.get("enemies", [])
            data["allies"] = entities.get("allies", [])
            data["boosters"] = entities.get("boosters", [])
            data["traps"] = entities.get("traps", [])
        elif hasattr(self.world, "grid") and hasattr(self.world.grid, "get_nearby"):
            # Try getting directly for tests/simulation
            if hasattr(self.ball, "x") and hasattr(self.ball, "y"):
                nearby = self.world.grid.get_nearby(self.ball.x, self.ball.y, radius)
                if hasattr(self.ball, "id"):
                    data["enemies"] = [b for b in nearby if b.id != self.ball.id]
                else:
                    data["enemies"] = nearby

            if hasattr(self.world, "boosters"):
                boosters = []
                for bo in self.world.boosters:
                    if bo.active:
                        dx = bo.x - self.ball.x
                        dy = bo.y - self.ball.y
                        if dx * dx + dy * dy <= radius * radius:
                            boosters.append(bo)
                data["boosters"] = boosters

            if hasattr(self.world, "traps"):
                traps = []
                for t in self.world.traps:
                    if t.active:
                        dx = t.x - self.ball.x
                        dy = t.y - self.ball.y
                        if dx * dx + dy * dy <= radius * radius:
                            traps.append(t)
                data["traps"] = traps
        else:
            # Maybe the data was passed directly for basic tests
            if hasattr(self.world, "entities"):
                data["enemies"] = self.world.entities.get("enemies", [])
                data["allies"] = self.world.entities.get("allies", [])
                data["boosters"] = self.world.entities.get("boosters", [])
                data["traps"] = self.world.entities.get("traps", [])

        # Process entities with distances
        ball_x = getattr(self.ball, "x", 0.0)
        ball_y = getattr(self.ball, "y", 0.0)

        # Sort entities by distance
        if data["enemies"] and hasattr(data["enemies"][0], "x"):
            data["enemies"].sort(key=lambda e: (getattr(e, "x", 0.0) - ball_x)**2 + (getattr(e, "y", 0.0) - ball_y)**2)
            if data["enemies"]:
                data["nearest_enemy"] = data["enemies"][0]

        if data["boosters"] and hasattr(data["boosters"][0], "x"):
            data["boosters"].sort(key=lambda b: (getattr(b, "x", 0.0) - ball_x)**2 + (getattr(b, "y", 0.0) - ball_y)**2)
            if data["boosters"]:
                data["nearest_booster"] = data["boosters"][0]

        if data["allies"] and hasattr(data["allies"][0], "x"):
            data["allies"].sort(key=lambda a: (getattr(a, "x", 0.0) - ball_x)**2 + (getattr(a, "y", 0.0) - ball_y)**2)
            if data["allies"]:
                data["nearest_ally"] = data["allies"][0]

        # Threat/Opportunity calculation
        enemies_count = len(data["enemies"])
        boosters_count = len(data["boosters"])
        allies_count = len(data["allies"])

        data["danger_level"] = enemies_count * 0.2
        data["opportunity_level"] = boosters_count * 0.3 + allies_count * 0.1

        return data
