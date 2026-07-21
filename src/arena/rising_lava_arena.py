import math
import random
from typing import Tuple

from arena.procedural_arena import ProceduralArena, Room, Corridor, Hazard

class RisingLavaArena(ProceduralArena):
    def __init__(self, arena_size: float = 2000.0, num_rooms: int = 5, seed: int | None = None):
        self.boundary_states = {"top": "bouncy", "bottom": "bouncy", "left": "bouncy", "right": "bouncy"}
        self.boundary_health = {"top": 2000.0, "bottom": 2000.0, "left": 2000.0, "right": 2000.0}

        self.lava_level = arena_size
        self.lava_rise_speed = 10.0

        super().__init__(arena_size=arena_size, num_rooms=num_rooms, seed=seed)

    def generate(self):
        super().generate()
        self.rooms.clear()
        self.corridors.clear()
        self.hazards.clear()

        w, h = self.width, self.height

        # Start platform
        self.rooms.append(Room(w/2 - 200, h - 300, 400, 200))

        for i in range(15):
            rw = random.uniform(150, 300)
            rh = random.uniform(100, 200)
            rx = random.uniform(50, w - rw - 50)
            ry = random.uniform(50, h - 400)

            overlap = False
            for r in self.rooms:
                if not (rx + rw + 20 < r.x or rx > r.x + r.width + 20 or
                        ry + rh + 20 < r.y or ry > r.y + r.height + 20):
                    overlap = True
                    break

            if not overlap:
                self.rooms.append(Room(rx, ry, rw, rh))

    def update_zone(self, current_tick: int, delta: float):
        is_new_tick = current_tick != self.last_tick
        super().update_zone(current_tick, delta)

        if is_new_tick:
            self.lava_level -= self.lava_rise_speed * delta

            if self.lava_level < 0:
                self.lava_level = 0.0

            surviving_rooms = []
            for r in self.rooms:
                if r.y < self.lava_level:
                    surviving_rooms.append(r)
            self.rooms = surviving_rooms

            # Create circular hazards to represent the lava line visually and deal damage
            # We can clear old rising_lava hazards and spawn new ones along the lava_level line
            self.hazards = [h for h in self.hazards if getattr(h, "kind", "") != "rising_lava_zone"]

            if self.lava_level < self.height:
                num_hazards = int(math.ceil(self.width / 200.0))
                for i in range(num_hazards):
                    hx = i * 200.0 + 100.0
                    hy = self.lava_level + 100.0 # Center below the lava level
                    # If hy is beyond height, we still create it to cover the bottom
                    h_id = 20000 + len(self.hazards) + i
                    h = Hazard(id=h_id, x=hx, y=hy, radius=120.0, kind="rising_lava_zone", damage=50.0)
                    self.hazards.append(h)

    def is_point_inside(self, x: float, y: float, radius: float) -> bool:
        return super().is_point_inside(x, y, radius)
