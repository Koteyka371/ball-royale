import random
import math
from typing import Any, List
from ai.game_modes import GameMode, GAME_MODES

class RandomTeleporterMode(GameMode):
    def __init__(self):
        super().__init__()
        self.name = "Random Teleporter"
        self.description = "Periodically, portals randomly appear on the map and teleport balls to random locations, breaking positioning strategies."
        self.portals = []
        self.spawn_timer = 0.0
        self.spawn_interval = 5.0

    def tick(self, world: Any, balls: List[Any], delta: float = 0.016) -> None:
        super().tick(world, balls, delta)

        arena_w = getattr(world.arena, "width", 800) if hasattr(world, "arena") and world.arena else 800
        arena_h = getattr(world.arena, "height", 600) if hasattr(world, "arena") and world.arena else 600

        self.spawn_timer += delta
        if self.spawn_timer >= self.spawn_interval:
            self.spawn_timer -= self.spawn_interval
            portal = {
                "x": random.uniform(50, max(50, arena_w - 50)),
                "y": random.uniform(50, max(50, arena_h - 50)),
                "radius": 30.0,
                "lifetime": 10.0
            }
            self.portals.append(portal)
            if hasattr(world, "add_event"):
                world.add_event("portal_spawn", {"message": "A random teleporter portal appeared!", "x": portal["x"], "y": portal["y"]})

        active_portals = []
        for portal in self.portals:
            portal["lifetime"] -= delta
            if portal["lifetime"] > 0:
                active_portals.append(portal)
        self.portals = active_portals

        for portal in self.portals:
            px, py, pr = portal["x"], portal["y"], portal["radius"]
            for b in balls:
                if getattr(b, "alive", False):
                    dx = getattr(b, "x", 0.0) - px
                    dy = getattr(b, "y", 0.0) - py
                    dist = math.sqrt(dx * dx + dy * dy)
                    if dist < pr + getattr(b, "radius", 10.0):
                        # Teleport
                        if hasattr(world, "add_event"):
                            world.add_event("teleport_out", {"message": "Teleported!", "x": b.x, "y": b.y})

                        # Reset velocity to 0
                        if hasattr(b, "vx"): b.vx = 0.0
                        if hasattr(b, "vy"): b.vy = 0.0

                        b.x = random.uniform(50, max(50, arena_w - 50))
                        b.y = random.uniform(50, max(50, arena_h - 50))

                        if hasattr(world, "add_event"):
                            world.add_event("teleport_in", {"message": "Arrived!", "x": b.x, "y": b.y})

GAME_MODES['random_teleporter'] = RandomTeleporterMode()
