import math
from typing import Tuple
from arena.basic_arena import BasicArena

class MorphingArena(BasicArena):
    def __init__(self, arena_size: float = 2000.0, seed=None):
        super().__init__(arena_size=arena_size, seed=seed)
        self.morph_timer = 0.0
        self.morph_duration = 60.0
        self.current_shape_idx = 0
        self.target_shape_idx = 0
        self.transition_progress = 0.0

    def get_sdf(self, x: float, y: float, r: float, shape_idx: int) -> float:
        cx, cy = self.width / 2.0, self.height / 2.0
        dx, dy = x - cx, y - cy

        # Shapes: 0=Square, 1=Circle, 2=Cross
        if shape_idx == 0:
            # Square SDF
            adx = abs(dx) - r
            ady = abs(dy) - r
            return math.hypot(max(adx, 0), max(ady, 0)) + min(max(adx, ady), 0)
        elif shape_idx == 1:
            # Circle SDF
            return math.hypot(dx, dy) - r
        elif shape_idx == 2:
            # Cross SDF
            w, h = r, r / 3.0

            adx1, ady1 = abs(dx) - w, abs(dy) - h
            d1 = math.hypot(max(adx1, 0), max(ady1, 0)) + min(max(adx1, ady1), 0)

            adx2, ady2 = abs(dx) - h, abs(dy) - w
            d2 = math.hypot(max(adx2, 0), max(ady2, 0)) + min(max(adx2, ady2), 0)

            return min(d1, d2)
        return 0.0

    def evaluate_sdf(self, x: float, y: float, base_radius: float) -> float:
        d1 = self.get_sdf(x, y, base_radius, self.current_shape_idx)
        d2 = self.get_sdf(x, y, base_radius, self.target_shape_idx)
        return d1 * (1.0 - self.transition_progress) + d2 * self.transition_progress

    def update_zone(self, current_tick: int, delta: float):
        super().update_zone(current_tick, delta)
        self.morph_timer += delta

        # Every 60 seconds, change shape
        # The transition takes 5 seconds, and then it stays for 55 seconds
        cycle_time = self.morph_timer % self.morph_duration

        cycle_idx = int(self.morph_timer / self.morph_duration)
        self.current_shape_idx = cycle_idx % 3
        self.target_shape_idx = (cycle_idx + 1) % 3

        # Transition during the first 10 seconds of the 60s cycle
        if cycle_time < 10.0:
            self.transition_progress = cycle_time / 10.0
        else:
            self.transition_progress = 1.0

    def is_point_inside(self, x: float, y: float, radius: float) -> bool:
        # Check base bounding box
        if not super().is_point_inside(x, y, radius):
            return False

        # Check SDF
        base_r = self.width / 2.0 - 100.0  # margin
        dist = self.evaluate_sdf(x, y, base_r)
        return dist <= -radius + 1.0

    def clamp_position(self, x: float, y: float, radius: float) -> Tuple[float, float, bool]:
        new_x, new_y, bounced = super().clamp_position(x, y, radius)

        base_r = self.width / 2.0 - 100.0
        dist = self.evaluate_sdf(new_x, new_y, base_r)

        if dist > -radius + 1.0:
            eps = 0.1
            gx = self.evaluate_sdf(new_x + eps, new_y, base_r) - self.evaluate_sdf(new_x - eps, new_y, base_r)
            gy = self.evaluate_sdf(new_x, new_y + eps, base_r) - self.evaluate_sdf(new_x, new_y - eps, base_r)
            length = math.hypot(gx, gy)

            if length > 0.0001:
                gx /= length
                gy /= length
                push_dist = dist + radius
                new_x -= gx * push_dist
                new_y -= gy * push_dist
            else:
                cx, cy = self.width / 2.0, self.height / 2.0
                dir_x, dir_y = cx - new_x, cy - new_y
                l = math.hypot(dir_x, dir_y)
                if l > 0.0001:
                    new_x += (dir_x/l) * 5.0
                    new_y += (dir_y/l) * 5.0

            bounced = True

        return new_x, new_y, bounced
