import random
import math
from typing import Any, List
from ai.game_modes import GameMode, GAME_MODES

class RandomPortalsMode(GameMode):
    def __init__(self):
        super().__init__()
        self.name = "Random Portals"
        self.description = "Portals appear across the map. Balls entering a portal exit immediately from a random other portal, maintaining their velocity. The portals change locations every 20 seconds."
        self.portals = []
        self.teleport_timer = 0.0
        self.teleport_interval = 20.0
        self.max_portals = 4

    def setup(self, world, balls):
        super().setup(world, balls)
        self.teleport_timer = 0.0
        self._spawn_portals(world)

    def _spawn_portals(self, world):
        self.portals = []
        arena_w = getattr(world.arena, "width", 800) if hasattr(world, "arena") and world.arena else 800
        arena_h = getattr(world.arena, "height", 600) if hasattr(world, "arena") and world.arena else 600
        for _ in range(self.max_portals):
            self.portals.append({
                "x": random.uniform(100, max(100, arena_w - 100)),
                "y": random.uniform(100, max(100, arena_h - 100)),
                "radius": 40.0
            })
        if hasattr(world, "add_event"):
            world.add_event("random_portals_spawn", {"message": "New portals have appeared!"})

    def tick(self, world: Any, balls: List[Any], delta: float = 0.016) -> None:
        super().tick(world, balls, delta)

        if not self.portals:
            self._spawn_portals(world)

        self.teleport_timer += delta
        if self.teleport_timer >= self.teleport_interval:
            self.teleport_timer -= self.teleport_interval
            self._spawn_portals(world)

        # Process collisions with balls
        for b in balls:
            if not getattr(b, "alive", False):
                continue

            bx = getattr(b, "x", 0.0)
            by = getattr(b, "y", 0.0)
            br = getattr(b, "radius", 10.0)

            for portal in self.portals:
                px, py, pr = portal["x"], portal["y"], portal["radius"]

                dx = bx - px
                dy = by - py
                dist = math.hypot(dx, dy)

                if dist < pr + br:
                    other_portals = [p for p in self.portals if p != portal]
                    if not other_portals:
                        continue

                    target_portal = random.choice(other_portals)

                    vx = getattr(b, "vx", 0.0)
                    vy = getattr(b, "vy", 0.0)
                    speed = math.hypot(vx, vy)

                    if speed > 0:
                        nx, ny = vx / speed, vy / speed
                    else:
                        nx, ny = 1.0, 0.0

                    offset_dist = target_portal["radius"] + br + 5.0

                    b.x = target_portal["x"] + nx * offset_dist
                    b.y = target_portal["y"] + ny * offset_dist

                    # Update bx, by to avoid multi-portal collisions in the same frame
                    bx = b.x
                    by = b.y

                    if hasattr(world, "add_event"):
                        world.add_event("random_portal_teleport", {"x": target_portal["x"], "y": target_portal["y"]})

                    break
