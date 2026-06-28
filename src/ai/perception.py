import math
from typing import Any, Dict

class Perception:
    """
    Perception system that scans the world for nearby entities:
    enemies, allies, boosters, and traps.
    Calculates distances, threat levels, and opportunity scores.
    """

    def __init__(self, ball: Any, world: Any):
        self.ball = ball
        self.world = world

    def scan(self) -> Dict[str, Any]:
        """
        Scans the environment within the ball's perception radius.
        Returns a dictionary with entities, distances, and scores.
        """
        perception_radius = getattr(self.ball, "perception_radius", 300.0)

        if hasattr(self.world, "arena") and getattr(self.world.arena, "is_night", None) is not None:
            if self.world.arena.is_night:
                perception_radius = min(perception_radius, 100.0)
            else:
                perception_radius = max(perception_radius, 2000.0)

        data: Dict[str, Any] = {
            "enemies": [],
            "allies": [],
            "boosters": [],
            "traps": [],
            "distances": {}, # Maps entity id to distance
            "threat_level": 0.0,
            "opportunity_score": 0.0,
            "coach_strategy": "",
            # For backward compatibility with existing layers
            "danger_level": 0.0,
            "opportunity_level": 0.0,
            "rival_spotted": False,
        }

        if not self.world or not hasattr(self.world, "get_nearby_entities"):
            return data

        entities = self.world.get_nearby_entities(self.ball, perception_radius)
        data["enemies"] = entities.get("enemies", [])
        data["allies"] = entities.get("allies", [])
        data["boosters"] = entities.get("boosters", [])
        data["traps"] = entities.get("traps", [])

        # Calculate distances and scores
        threat = 0.0
        opp = 0.0

        bx, by = getattr(self.ball, "x", 0), getattr(self.ball, "y", 0)

        # Helper to compute distance
        def calc_dist(ent):
            ex, ey = getattr(ent, "x", 0), getattr(ent, "y", 0)
            dx = ex - bx
            dy = ey - by
            return math.sqrt(dx * dx + dy * dy)

        # Include procedural hazards within perception radius
        if hasattr(self.world, "arena") and hasattr(self.world.arena, "hazards"):
            import random
            for h in self.world.arena.hazards:
                dist = calc_dist(h)
                # Check if within perception radius and not already in traps
                if dist <= perception_radius:
                    if getattr(h, "kind", "") == "fake_booster":
                        is_scout = getattr(self.ball, "ball_type", "") == "scout"
                        perception_score = getattr(self.ball, "perception_score", 0.0)

                        identified = False
                        if is_scout:
                            if perception_score > 50 or random.random() < 0.3:
                                identified = True

                        if identified:
                            if not any(getattr(t, "id", None) == h.id for t in data["traps"]):
                                data["traps"].append(h)
                        else:
                            if not any(getattr(b, "id", None) == h.id for b in data["boosters"]):
                                data["boosters"].append(h)
                    else:
                        # Make sure it's not already in there by id
                        if not any(getattr(t, "id", None) == h.id for t in data["traps"]):
                            data["traps"].append(h)

        for enemy in data["enemies"]:
            dist = calc_dist(enemy)
            if hasattr(enemy, "id"):
                data["distances"][enemy.id] = dist

                # Ball Relationships - Balls remember each other


                # Rivalry skill: attacked me before -> attack on sight
                if hasattr(self.ball, "memory"):
                    ball_mem = self.ball.memory.get(enemy.id, {})
                    if ball_mem.get("relation") == "rival":
                        data["rival_spotted"] = True

            # Threat increases if enemy is closer. Max threat from one enemy = 1.0 (at dist 0)
            threat += max(0.0, 1.0 - (dist / perception_radius)) * 1.5

        for trap in data["traps"]:
            dist = calc_dist(trap)
            if hasattr(trap, "id"):
                data["distances"][trap.id] = dist
            threat += max(0.0, 1.0 - (dist / perception_radius)) * 2.0

        for booster in data["boosters"]:
            dist = calc_dist(booster)
            if hasattr(booster, "id"):
                data["distances"][booster.id] = dist
            opp += max(0.0, 1.0 - (dist / perception_radius)) * 1.0

        team_messages = []

        for ally in data["allies"]:
            dist = calc_dist(ally)
            if hasattr(ally, "id"):
                data["distances"][ally.id] = dist
            opp += max(0.0, 1.0 - (dist / perception_radius)) * 0.5
            if hasattr(ally, "team_message") and ally.team_message:
                team_messages.append(ally.team_message)

        data["threat_level"] = threat
        data["opportunity_score"] = opp

        # Coach Mode
        if hasattr(self.world, "coach_strategy") and self.world.coach_strategy:
            strat = self.world.coach_strategy
            if isinstance(strat, dict):
                team = getattr(self.ball, "team", getattr(self.ball, "ball_type", ""))
                if team in strat:
                    data["coach_strategy"] = strat[team]
            elif isinstance(strat, str):
                data["coach_strategy"] = strat


        # Backward compatibility for existing logic
        data["danger_level"] = len(data["enemies"]) * 0.2
        data["opportunity_level"] = len(data["boosters"]) * 0.3 + len(data["allies"]) * 0.1
        data["team_messages"] = team_messages

        return data
