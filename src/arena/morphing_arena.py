import math
from typing import Tuple
from arena.procedural_arena import ProceduralArena

def sdf_box(px: float, py: float, width: float, height: float) -> float:
    dx = abs(px) - width / 2.0
    dy = abs(py) - height / 2.0
    return math.hypot(max(dx, 0.0), max(dy, 0.0)) + min(max(dx, dy), 0.0)

def sdf_cross(px: float, py: float, span: float, thickness: float) -> float:
    d1 = sdf_box(px, py, thickness, span)
    d2 = sdf_box(px, py, span, thickness)
    return min(d1, d2)

def sdf_circle(px: float, py: float, radius: float) -> float:
    return math.hypot(px, py) - radius

class MorphingArena(ProceduralArena):
    def __init__(self, arena_size: float = 2000.0, seed: int | None = None):
        super().__init__(arena_size=arena_size, num_rooms=0, seed=seed)
        self.boundary_states = {"top": "bouncy", "bottom": "bouncy", "left": "bouncy", "right": "bouncy"}
        self.boundary_health = {"top": 2000.0, "bottom": 2000.0, "left": 2000.0, "right": 2000.0}
        self.current_tick = 0
        self.name = "morphing"

    def generate(self):
        super().generate()
        self.rooms.clear()
        self.corridors.clear()

    def get_sdf(self, x: float, y: float) -> float:
        phase = (self.current_tick % 3600) / 3600.0

        cx, cy = self.width / 2.0, self.height / 2.0
        px, py = x - cx, y - cy

        size = min(self.width, self.height) - 100.0

        shapes = [
            sdf_box(px, py, size, size),
            sdf_circle(px, py, size / 2.0),
            sdf_cross(px, py, size, size * 0.4)
        ]

        idx1 = int(phase * 3)
        idx2 = (idx1 + 1) % 3
        t = (phase * 3) - idx1

        t = t * t * (3.0 - 2.0 * t)

        return (1.0 - t) * shapes[idx1] + t * shapes[idx2]

    def is_point_inside(self, x: float, y: float, radius: float) -> bool:
        return self.get_sdf(x, y) <= -radius + 1.0

    def clamp_position(self, x: float, y: float, radius: float) -> Tuple[float, float, bool]:
        val = self.get_sdf(x, y)
        if val <= -radius + 1.0:
            return x, y, False

        new_x, new_y = x, y
        eps = 1.0

        for _ in range(30):
            val = self.get_sdf(new_x, new_y)
            if val <= -radius + 1.0:
                break

            dx = self.get_sdf(new_x + eps, new_y) - self.get_sdf(new_x - eps, new_y)
            dy = self.get_sdf(new_x, new_y + eps) - self.get_sdf(new_x, new_y - eps)
            gl = math.hypot(dx, dy)

            if gl > 0.0001:
                nx, ny = dx / gl, dy / gl
            else:
                cx, cy = self.width / 2.0, self.height / 2.0
                vec_x, vec_y = cx - new_x, cy - new_y
                vec_len = math.hypot(vec_x, vec_y)
                if vec_len > 0.0001:
                    nx, ny = -vec_x / vec_len, -vec_y / vec_len
                else:
                    nx, ny = 1.0, 0.0

            move = (val + radius) * 0.9
            new_x -= nx * move
            new_y -= ny * move

        return new_x, new_y, True

    def update_zone(self, current_tick: int, delta: float):
        self.current_tick = current_tick
        super().update_zone(current_tick, delta)

        if hasattr(self, "hazards"):
            for hazard in self.hazards:
                hx, hy, bounced = self.clamp_position(hazard.x, hazard.y, getattr(hazard, "radius", 0.0))
                if bounced:
                    hazard.x = hx
                    hazard.y = hy

        if hasattr(self, "platforms"):
            for platform in self.platforms:
                rad = min(getattr(platform, "width", 0.0), getattr(platform, "height", 0.0)) / 2.0
                px, py, bounced = self.clamp_position(platform.x, platform.y, rad)
                if bounced:
                    platform.x = px
                    platform.y = py
