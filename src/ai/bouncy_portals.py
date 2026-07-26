
import random
import math
from typing import Any, List
from ai.game_modes import GameMode, GAME_MODES

class BouncyPortalsMode(GameMode):
    def __init__(self):
        super().__init__()
        self.name = "Bouncy Portals"
        self.description = "Portals spawn on the map that reflect projectiles and players based on velocity and incidence angle, turning the arena into a bouncy chaos."
        self.portals = []
        self.spawn_timer = 0.0
        self.spawn_interval = 4.0
        self.max_portals = 5

    def tick(self, world: Any, balls: List[Any], delta: float = 0.016) -> None:
        super().tick(world, balls, delta)

        arena_w = getattr(world.arena, "width", 800) if hasattr(world, "arena") and world.arena else 800
        arena_h = getattr(world.arena, "height", 600) if hasattr(world, "arena") and world.arena else 600

        self.spawn_timer += delta
        if self.spawn_timer >= self.spawn_interval and len(self.portals) < self.max_portals:
            self.spawn_timer -= self.spawn_interval

            # Spawn portal at a random angle
            angle = random.uniform(0, 2 * math.pi)
            # Normal vector pointing OUT from the portal face
            nx = math.cos(angle)
            ny = math.sin(angle)

            portal = {
                "x": random.uniform(100, max(100, arena_w - 100)),
                "y": random.uniform(100, max(100, arena_h - 100)),
                "radius": 40.0,
                "nx": nx,
                "ny": ny,
                "lifetime": 15.0
            }
            self.portals.append(portal)
            if hasattr(world, "add_event"):
                world.add_event("bouncy_portal_spawn", {"x": portal["x"], "y": portal["y"]})

        active_portals = []
        for portal in self.portals:
            portal["lifetime"] -= delta
            if portal["lifetime"] > 0:
                active_portals.append(portal)
        self.portals = active_portals

        # Process collisions with balls
        for portal in self.portals:
            px, py, pr, nx, ny = portal["x"], portal["y"], portal["radius"], portal["nx"], portal["ny"]
            for b in balls:
                if not getattr(b, "alive", False):
                    continue

                bx = getattr(b, "x", 0.0)
                by = getattr(b, "y", 0.0)
                br = getattr(b, "radius", 10.0)
                bvx = getattr(b, "vx", 0.0)
                bvy = getattr(b, "vy", 0.0)

                dx = bx - px
                dy = by - py
                dist = math.hypot(dx, dy)

                if dist < pr + br:
                    # Determine if it's hitting the portal from the front or back
                    dot_product = dx * nx + dy * ny
                    vel_dot_normal = bvx * nx + bvy * ny

                    # Only bounce if they are moving TOWARDS the portal face (opposite to normal)
                    if vel_dot_normal < 0:
                        # Reflection vector: V - 2(V dot N) * N
                        # Adding a bounce multiplier for extra chaos
                        bounce_mult = 1.5
                        new_vx = bvx - 2 * vel_dot_normal * nx
                        new_vy = bvy - 2 * vel_dot_normal * ny

                        b.vx = new_vx * bounce_mult
                        b.vy = new_vy * bounce_mult

                        # Push outside to prevent sticking
                        overlap = (pr + br) - dist
                        push_nx = dx / dist if dist > 0 else nx
                        push_ny = dy / dist if dist > 0 else ny

                        b.x = bx + push_nx * overlap
                        b.y = by + push_ny * overlap

                        if hasattr(world, "add_event"):
                            world.add_event("portal_bounce", {"x": px, "y": py})

        # Process collisions with hazards (projectiles)
        if hasattr(world, "arena") and hasattr(world.arena, "hazards"):
            for portal in self.portals:
                px, py, pr, nx, ny = portal["x"], portal["y"], portal["radius"], portal["nx"], portal["ny"]
                for h in world.arena.hazards:
                    if not getattr(h, "active", True):
                        continue

                    hx = getattr(h, "x", 0.0)
                    hy = getattr(h, "y", 0.0)
                    hr = getattr(h, "radius", 10.0)
                    hvx = getattr(h, "vx", 0.0)
                    hvy = getattr(h, "vy", 0.0)

                    dx = hx - px
                    dy = hy - py
                    dist = math.hypot(dx, dy)

                    if dist < pr + hr:
                        vel_dot_normal = hvx * nx + hvy * ny

                        # Only bounce if moving
                        if (abs(hvx) > 0.1 or abs(hvy) > 0.1) and vel_dot_normal < 0:
                            new_vx = hvx - 2 * vel_dot_normal * nx
                            new_vy = hvy - 2 * vel_dot_normal * ny

                            setattr(h, "vx", new_vx)
                            setattr(h, "vy", new_vy)

                            overlap = (pr + hr) - dist
                            push_nx = dx / dist if dist > 0 else nx
                            push_ny = dy / dist if dist > 0 else ny

                            setattr(h, "x", hx + push_nx * overlap)
                            setattr(h, "y", hy + push_ny * overlap)

                            if hasattr(world, "add_event"):
                                world.add_event("portal_bounce", {"x": px, "y": py})

GAME_MODES['bouncy_portals'] = BouncyPortalsMode()
