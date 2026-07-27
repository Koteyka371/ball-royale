import math
import random
from ai.game_modes import GameMode

class AcousticDisruptionFieldMode(GameMode):
    def __init__(self):
        super().__init__()
        self.name = "Acoustic Disruption Field"
        self.description = "A new hazard that temporarily disables the perception_radius of any ball inside it, rendering them effectively blind and unable to target enemies, but still able to move freely."
        self.event_timer = 0.0

    def tick(self, world, balls, delta=0.016):
        self.event_timer += delta

        if not hasattr(world, "arena"):
            return

        if not hasattr(world.arena, "hazards"):
            world.arena.hazards = []

        # Spawn hazard periodically
        if self.event_timer >= 15.0:
            self.event_timer = 0.0
            arena_width = getattr(world.arena, "width", 1000)
            arena_height = getattr(world.arena, "height", 1000)
            cx = random.uniform(200, arena_width - 200)
            cy = random.uniform(200, arena_height - 200)

            try:
                from arena.procedural_arena import Hazard
                h = Hazard(id=len(world.arena.hazards) + 98000 + random.randint(0, 1000), x=cx, y=cy, radius=100.0, kind="acoustic_disruption", damage=0.0)
            except ImportError:
                class DummyHazardAD:
                    def __init__(self, id, x, y, radius, kind, damage):
                        self.id = id
                        self.x = x
                        self.y = y
                        self.radius = radius
                        self.kind = kind
                        self.damage = damage
                        self.active = True
                h = DummyHazardAD(id=len(world.arena.hazards) + 98000 + random.randint(0, 1000), x=cx, y=cy, radius=100.0, kind="acoustic_disruption", damage=0.0)

            h.duration = 10.0
            world.arena.hazards.append(h)

        # Apply hazard logic
        active_hazards = []
        for h in world.arena.hazards:
            if getattr(h, "kind", "") == "acoustic_disruption":
                h.duration = getattr(h, "duration", 10.0) - delta
                if h.duration > 0:
                    active_hazards.append(h)
                    # apply blindness
                    for b in balls:
                        if not getattr(b, "alive", True):
                            continue
                        dist_sq = (b.x - h.x)**2 + (b.y - h.y)**2
                        # Check if inside
                        b_rad = getattr(b, "radius", 10.0)
                        if dist_sq < (getattr(h, "radius", 100.0) + b_rad)**2:
                            # Blind the ball
                            if not getattr(b, "is_acoustically_blinded", False):
                                b.is_acoustically_blinded = True
                                if not hasattr(b, "base_perception_radius_acoustic"):
                                    b.base_perception_radius_acoustic = getattr(b, "perception_radius", 250.0)
                                b.perception_radius = 0.0
                            b.acoustic_blind_timer = 0.2
            else:
                active_hazards.append(h)
        world.arena.hazards = active_hazards

        # Tick down the timer
        for b in balls:
            if getattr(b, "is_acoustically_blinded", False):
                b.acoustic_blind_timer = getattr(b, "acoustic_blind_timer", 0.0) - delta
                if b.acoustic_blind_timer <= 0:
                    b.is_acoustically_blinded = False
                    if hasattr(b, "base_perception_radius_acoustic"):
                        b.perception_radius = b.base_perception_radius_acoustic
                        delattr(b, "base_perception_radius_acoustic")
