import math
import random
from typing import Tuple

from arena.procedural_arena import ProceduralArena

class ShrinkingMapsArena(ProceduralArena):
    def __init__(self, arena_size: float = 2000.0, num_rooms: int = 5, seed: int | None = None):
        self.boundary_states = {"top": "bouncy", "bottom": "bouncy", "left": "bouncy", "right": "bouncy"}
        self.boundary_health = {"top": 2000.0, "bottom": 2000.0, "left": 2000.0, "right": 2000.0}
        super().__init__(arena_size=arena_size, num_rooms=num_rooms, seed=seed)
        self.min_x = 0.0
        self.min_y = 0.0
        self.max_x = self.width
        self.max_y = self.height

    def update_zone(self, current_tick: int, delta: float):
        is_new_tick = current_tick != self.last_tick

        super().update_zone(current_tick, delta)

        if is_new_tick:
            # Shrink map boundaries inward
            shrink_rate = 10.0 * delta

            # Ensure min and max don't cross each other and keep a minimal map size (e.g. 50x50)
            if self.max_x - self.min_x > 50.0:
                self.min_x += shrink_rate
                self.max_x -= shrink_rate

            if self.max_y - self.min_y > 50.0:
                self.min_y += shrink_rate
                self.max_y -= shrink_rate

            # Clamp all hazards and platforms to the new boundaries
            if hasattr(self, "hazards"):
                for hazard in self.hazards:
                    hazard.x = max(self.min_x + hazard.radius, min(self.max_x - hazard.radius, hazard.x))
                    hazard.y = max(self.min_y + hazard.radius, min(self.max_y - hazard.radius, hazard.y))

            if hasattr(self, "platforms"):
                for platform in self.platforms:
                    pw_half = platform.width / 2
                    ph_half = platform.height / 2
                    platform.x = max(self.min_x + pw_half, min(self.max_x - pw_half, platform.x))
                    platform.y = max(self.min_y + ph_half, min(self.max_y - ph_half, platform.y))

    def is_point_inside(self, x: float, y: float, radius: float) -> bool:
        # Check against physical shrinking boundaries
        if not (self.min_x + radius <= x <= self.max_x - radius and self.min_y + radius <= y <= self.max_y - radius):
            return False

        # Call the procedural arena logic
        return super().is_point_inside(x, y, radius)

    def clamp_position(self, x: float, y: float, radius: float) -> Tuple[float, float, bool]:
        bounced = False
        new_x = x
        new_y = y

        # Hard clamp against shrinking boundaries first
        if new_x < self.min_x + radius:
            new_x = self.min_x + radius
            bounced = True
        elif new_x > self.max_x - radius:
            new_x = self.max_x - radius
            bounced = True

        if new_y < self.min_y + radius:
            new_y = self.min_y + radius
            bounced = True
        elif new_y > self.max_y - radius:
            new_y = self.max_y - radius
            bounced = True

        # Delegate remaining logic to ProceduralArena (which checks safe zone, rooms, corridors)
        res_x, res_y, proc_bounced = super().clamp_position(new_x, new_y, radius)

        # Ensure procedural clamp didn't push us outside the shrinking bounds
        final_x = max(self.min_x + radius, min(self.max_x - radius, res_x))
        final_y = max(self.min_y + radius, min(self.max_y - radius, res_y))

        if final_x != res_x or final_y != res_y:
            proc_bounced = True

        return final_x, final_y, bounced or proc_bounced
