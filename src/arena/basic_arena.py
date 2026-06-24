import random
from typing import Tuple

class BasicArena:
    def __init__(self, arena_size: float = 2000.0, seed: int | None = None):
        self.rng = random.Random(seed)
        self.width = arena_size
        self.height = arena_size

        # Shrinking zone
        self.safe_zone_radius = arena_size * 0.7
        self.safe_zone_center = (arena_size / 2, arena_size / 2)
        self.last_tick = -1
        self.danger_grid: dict[tuple[int, int], float] = {}

    def get_random_spawn_point(self, radius: float) -> Tuple[float, float]:
        return (self.rng.uniform(radius, self.width - radius),
                self.rng.uniform(radius, self.height - radius))

    def is_point_inside(self, x: float, y: float, radius: float) -> bool:
        return (radius <= x <= self.width - radius and
                radius <= y <= self.height - radius)

    def clamp_position(self, x: float, y: float, radius: float) -> Tuple[float, float, bool]:
        bounced = False
        new_x = x
        new_y = y

        if x < radius:
            new_x = radius
            bounced = True
        elif x > self.width - radius:
            new_x = self.width - radius
            bounced = True

        if y < radius:
            new_y = radius
            bounced = True
        elif y > self.height - radius:
            new_y = self.height - radius
            bounced = True

        return new_x, new_y, bounced

    def update_zone(self, current_tick: int, delta: float):
        if current_tick != self.last_tick:
            self.last_tick = current_tick
            self.safe_zone_radius -= 10.0 * delta
            if self.safe_zone_radius < 50.0:
                self.safe_zone_radius = 50.0
