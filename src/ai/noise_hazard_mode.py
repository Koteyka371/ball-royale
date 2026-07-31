import math
import random
from ai.game_modes import GameMode

class NoiseHazardMode(GameMode):
    def __init__(self):
        super().__init__()
        self.name = "Noise Hazard"
        self.description = "Spawns a hazard that pulses and damages players around it based on how fast they are moving (noise)."
        self.spawn_timer = 5.0

    def tick(self, world, balls, delta=0.016):
        self.spawn_timer -= delta

        if not hasattr(world, "arena"):
            return

        if not hasattr(world.arena, "hazards"):
            world.arena.hazards = []

        if self.spawn_timer <= 0:
            self.spawn_timer = 15.0
            arena_width = getattr(world.arena, "width", 1000)
            arena_height = getattr(world.arena, "height", 1000)
            cx = random.uniform(200, arena_width - 200)
            cy = random.uniform(200, arena_height - 200)

            try:
                from arena.procedural_arena import Hazard
                h = Hazard(id=len(world.arena.hazards) + 98500 + random.randint(0, 1000), x=cx, y=cy, radius=30.0, kind="noise_hazard", damage=0.0)
            except ImportError:
                class DummyHazardNH:
                    def __init__(self, id, x, y, radius, kind, damage):
                        self.id = id
                        self.x = x
                        self.y = y
                        self.radius = radius
                        self.kind = kind
                        self.damage = damage
                        self.active = True
                h = DummyHazardNH(id=len(world.arena.hazards) + 98500 + random.randint(0, 1000), x=cx, y=cy, radius=30.0, kind="noise_hazard", damage=0.0)

            h.duration = 15.0
            h.pulse_timer = 2.0
            h.pulse_radius = 250.0
            world.arena.hazards.append(h)

        active_hazards = []
        for h in world.arena.hazards:
            if getattr(h, "kind", "") == "noise_hazard":
                h.duration = getattr(h, "duration", 15.0) - delta
                if h.duration > 0:
                    active_hazards.append(h)
                    h.pulse_timer = getattr(h, "pulse_timer", 2.0) - delta
                    if h.pulse_timer <= 0:
                        h.pulse_timer = 2.0
                        h_x = getattr(h, "x", 0.0)
                        h_y = getattr(h, "y", 0.0)
                        h_rad = getattr(h, "pulse_radius", 250.0)

                        ev = {"type": "visual_effect", "data": {"type": "noise_pulse", "x": h_x, "y": h_y, "radius": h_rad, "color": "orange", "duration": 0.5}}
                        if hasattr(world, "events"):
                            world.events.append(ev)
                        elif isinstance(world, dict) and "events" in world:
                            world["events"].append(ev)

                        for b in balls:
                            if not getattr(b, "alive", True):
                                continue
                            b_x = getattr(b, "x", 0.0)
                            b_y = getattr(b, "y", 0.0)
                            dist = math.hypot(b_x - h_x, b_y - h_y)
                            if dist < h_rad:
                                b_vx = getattr(b, "vx", 0.0)
                                b_vy = getattr(b, "vy", 0.0)
                                speed = math.hypot(b_vx, b_vy)

                                # Noise factor = speed. If stationary, ~0 noise. Max speed is typically 400-600.
                                # Base damage calculation based on speed
                                damage = speed * 0.1

                                # Let's say damage threshold so tiny movements don't deal damage
                                if damage > 2.0:
                                    if hasattr(world, "_deal_damage"):
                                        world._deal_damage(None, b, damage)
                                    else:
                                        b.hp = getattr(b, "hp", 100.0) - damage
            else:
                active_hazards.append(h)
        world.arena.hazards = active_hazards
