import math
import random
from typing import Any, List
from ai.game_modes import GameMode

BALL_TYPES_LIST = [
    "necromancer", "warrior", "tank", "assassin", "mirage",
    "nemesis_bomber", "paladin", "sniper", "medic", "rogue",
    "elementalist", "shuffler"
]

class ChaosArtifactMode(GameMode):
    def __init__(self):
        super().__init__()
        self.name = "Chaos Artifact"
        self.description = "An artifact spawns that gives a massive power boost to whoever holds it, but completely randomizes their abilities and ball type every 10 seconds."
        self.artifact = None
        self.holder_id = None
        self.artifact_timer = 0.0

    def setup(self, world: Any, balls: List[Any]) -> None:
        super().setup(world, balls)
        self.artifact = None
        self.holder_id = None
        self.artifact_timer = 0.0

    def tick(self, world: Any, balls: List[Any], delta: float = 0.016) -> None:
        super().tick(world, balls, delta)

        arena_w = getattr(world.arena, "width", 800) if hasattr(world, "arena") and world.arena else 800
        arena_h = getattr(world.arena, "height", 600) if hasattr(world, "arena") and world.arena else 600

        # Spawn artifact if it doesn't exist
        if self.artifact is None:
            self.artifact = {
                "x": random.uniform(50, arena_w - 50),
                "y": random.uniform(50, arena_h - 50),
                "radius": 15.0
            }
            if hasattr(world, "add_event"):
                world.add_event("chaos_artifact_spawned", {"x": self.artifact["x"], "y": self.artifact["y"]})
            self.holder_id = None
            self.artifact_timer = 0.0

        alive_balls = [b for b in balls if getattr(b, "alive", False)]

        # Check if holder died
        if self.holder_id is not None:
            holder = next((b for b in balls if getattr(b, "id", None) == self.holder_id), None)
            if not holder or not getattr(holder, "alive", False):
                # Drop artifact
                self.holder_id = None
                self.artifact_timer = 0.0
                if holder:
                    self.artifact["x"] = getattr(holder, "x", self.artifact["x"])
                    self.artifact["y"] = getattr(holder, "y", self.artifact["y"])
                if hasattr(world, "add_event"):
                    world.add_event("chaos_artifact_dropped", {"x": self.artifact["x"], "y": self.artifact["y"]})

        # If no holder, check collisions
        if self.holder_id is None:
            for b in alive_balls:
                bx = getattr(b, "x", 0.0)
                by = getattr(b, "y", 0.0)
                br = getattr(b, "radius", 10.0)

                dx = bx - self.artifact["x"]
                dy = by - self.artifact["y"]
                dist = math.hypot(dx, dy)

                if dist < br + self.artifact["radius"]:
                    self.holder_id = getattr(b, "id", None)
                    self.artifact_timer = 0.0
                    if hasattr(world, "add_event"):
                        world.add_event("chaos_artifact_picked_up", {"holder_id": self.holder_id})
                    break

        # If there is a holder, apply effects
        if self.holder_id is not None:
            holder = next((b for b in alive_balls if getattr(b, "id", None) == self.holder_id), None)
            if holder:
                # Keep artifact at holder's position (conceptually)
                self.artifact["x"] = getattr(holder, "x", self.artifact["x"])
                self.artifact["y"] = getattr(holder, "y", self.artifact["y"])

                # Apply massive power boost
                base_speed = getattr(holder, "base_speed", 100.0)
                holder.speed = base_speed * 2.0

                base_damage = getattr(holder, "base_damage", 10.0)
                holder.damage = base_damage * 3.0

                # Cosmetics
                cosmetics = getattr(holder, "cosmetics", [])
                if "chaos_aura" not in cosmetics:
                    cosmetics.append("chaos_aura")
                    holder.cosmetics = cosmetics

                # Timer for randomization
                self.artifact_timer += delta
                if self.artifact_timer >= 10.0:
                    self.artifact_timer -= 10.0

                    new_type = random.choice(BALL_TYPES_LIST)
                    holder.ball_type = new_type

                    if hasattr(world, "add_event"):
                        world.add_event("chaos_artifact_randomized", {"holder_id": self.holder_id, "new_type": new_type})
