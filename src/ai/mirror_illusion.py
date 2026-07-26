import math
from typing import Any, List
from ai.game_modes import GameMode

class MirrorIllusionMode(GameMode):
    def __init__(self):
        super().__init__()
        self.name = "Mirror Illusion"
        self.description = "A game mode where every ball has a harmless mirror illusion on the opposite side of the arena that moves symmetrically, confusing opponents and absorbing single-target projectiles."
        self.illusions = {}

    def setup(self, world: Any, balls: List[Any]) -> None:
        super().setup(world, balls)
        self.illusions = {}
        if not hasattr(world, "entities"):
            world.entities = []

    def tick(self, world: Any, balls: List[Any], delta: float = 0.016) -> None:
        super().tick(world, balls, delta)

        arena_w = getattr(world.arena, "width", 1000.0) if hasattr(world, "arena") and world.arena else 1000.0
        arena_h = getattr(world.arena, "height", 1000.0) if hasattr(world, "arena") and world.arena else 1000.0

        # Track active ball IDs to remove orphaned illusions
        active_ball_ids = set()

        for b in balls:
            b_id = getattr(b, "id", None)
            if b_id is None or getattr(b, "ball_type", None) == "spectator":
                continue

            is_alive = getattr(b, "alive", False)
            if not is_alive:
                continue

            active_ball_ids.add(b_id)

            # Ensure illusion exists
            if b_id not in self.illusions:
                illusion = {
                    "id": f"illusion_{b_id}",
                    "is_illusion": True,
                    "alive": True,
                    "x": arena_w - getattr(b, "x", arena_w / 2.0),
                    "y": arena_h - getattr(b, "y", arena_h / 2.0),
                    "vx": -getattr(b, "vx", 0.0),
                    "vy": -getattr(b, "vy", 0.0),
                    "radius": getattr(b, "radius", 10.0),
                    "team": getattr(b, "team", getattr(b, "ball_type", "unknown")),
                    "ball_type": "illusion",
                    "hp": 1.0,
                    "max_hp": 1.0,
                    "speed_multiplier": 1.0,
                    "damage_multiplier": 1.0,
                    "speed": 0.0,
                    "base_speed": 0.0,
                    "mass": getattr(b, "mass", 1.0)
                }
                self.illusions[b_id] = illusion
                if hasattr(world, "entities"):
                    world.entities.append(illusion)
                elif hasattr(world, "balls"):
                    world.balls.append(illusion)

            # Update illusion position
            illusion = self.illusions[b_id]
            illusion["x"] = arena_w - getattr(b, "x", arena_w / 2.0)
            illusion["y"] = arena_h - getattr(b, "y", arena_h / 2.0)
            illusion["vx"] = -getattr(b, "vx", 0.0)
            illusion["vy"] = -getattr(b, "vy", 0.0)
            illusion["radius"] = getattr(b, "radius", 10.0)
            illusion["team"] = getattr(b, "team", getattr(b, "ball_type", "unknown"))
            illusion["alive"] = True

        # Clean up orphaned illusions
        orphaned_ids = set(self.illusions.keys()) - active_ball_ids
        for b_id in orphaned_ids:
            illusion = self.illusions[b_id]
            illusion["alive"] = False
            if hasattr(world, "entities") and illusion in world.entities:
                world.entities.remove(illusion)
            elif hasattr(world, "balls") and illusion in world.balls:
                world.balls.remove(illusion)
            del self.illusions[b_id]

        # Absorb hazards/projectiles
        if hasattr(world, "arena") and hasattr(world.arena, "hazards"):
            hazards_to_remove = []
            for h in world.arena.hazards:
                if not getattr(h, "active", True):
                    continue

                hx = getattr(h, "x", 0.0)
                hy = getattr(h, "y", 0.0)
                hr = getattr(h, "radius", 10.0)

                # Check collision with illusions
                for b_id, illusion in self.illusions.items():
                    if not illusion["alive"]:
                        continue

                    # Ignore own team hazards if team info is available
                    h_team = getattr(h, "team", None)
                    if h_team and h_team == illusion["team"]:
                        continue

                    dx = hx - illusion["x"]
                    dy = hy - illusion["y"]
                    dist = math.hypot(dx, dy)

                    if dist < hr + illusion["radius"]:
                        hazards_to_remove.append(h)
                        break # Only absorb once

            for h in hazards_to_remove:
                if hasattr(h, "active"):
                    h.active = False
                if h in world.arena.hazards:
                    world.arena.hazards.remove(h)
