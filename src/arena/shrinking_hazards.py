import math
import random
from typing import Tuple

from arena.procedural_arena import ProceduralArena, Hazard

class ShrinkingHazardsArena(ProceduralArena):
    def __init__(self, arena_size: float = 2000.0, num_rooms: int = 5, seed: int | None = None):
        super().__init__(arena_size=arena_size, num_rooms=num_rooms, seed=seed)
        self.hazard_spawn_timer = 0.0

    def update_zone(self, current_tick: int, delta: float):
        # We need to process our logic if the tick is new.
        is_new_tick = current_tick != self.last_tick

        # Super class update_zone also sets self.last_tick to current_tick
        super().update_zone(current_tick, delta)

        if is_new_tick:
            self.hazard_spawn_timer += delta
            # Spawn a new expanding hazard on the edge of the safe zone every 5 seconds
            if self.hazard_spawn_timer >= 5.0:
                self.hazard_spawn_timer = 0.0

                # Pick a random angle
                angle = random.uniform(0, 2 * math.pi)

                # Place hazard on the current safe zone edge
                spawn_dist = self.safe_zone_radius
                cx, cy = self.safe_zone_center

                hx = cx + math.cos(angle) * spawn_dist
                hy = cy + math.sin(angle) * spawn_dist

                # Clamp position to arena bounds
                hx = max(0.0, min(self.width, hx))
                hy = max(0.0, min(self.height, hy))

                h_id = 10000 + len(self.hazards) + random.randint(0, 1000)
                # Create a hazard that starts small but expands over time
                # We'll use a type that causes damage, like "lava" or a custom "shrinking_zone_hazard"
                new_hazard = Hazard(id=h_id, x=hx, y=hy, radius=10.0, kind="shrinking_zone_hazard", damage=25.0)

                # The hazard will grow to cover a large area, effectively shrinking the playable space
                new_hazard.target_radius = 200.0

                self.hazards.append(new_hazard)

            # Manually expand our shrinking_zone_hazards if they haven't reached target radius
            for h in self.hazards:
                if getattr(h, "kind", "") == "shrinking_zone_hazard" and h.radius < getattr(h, "target_radius", 0.0):
                    # Grow slowly over time (e.g., reaching 200 radius in ~30 seconds)
                    grow_rate = 200.0 / 30.0
                    h.radius += grow_rate * delta
                    if h.radius > h.target_radius:
                        h.radius = h.target_radius
