from arena.procedural_arena import Hazard
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
        self.hazards = []

    def get_random_spawn_point(self, radius: float) -> Tuple[float, float]:
        return (self.rng.uniform(radius, self.width - radius),
                self.rng.uniform(radius, self.height - radius))

    def is_point_inside(self, x: float, y: float, radius: float) -> bool:
        if not (radius <= x <= self.width - radius and radius <= y <= self.height - radius):
            return False

        import math
        cx, cy = self.safe_zone_center
        sz_radius = self.safe_zone_radius
        dist = math.hypot(x - cx, y - cy)
        return dist <= sz_radius - radius

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

        import math
        cx, cy = self.safe_zone_center
        sz_radius = self.safe_zone_radius
        dist = math.hypot(new_x - cx, new_y - cy)

        # If outside the safe zone, push inwards towards safe zone edge
        if dist > sz_radius - radius:
            if dist > 0.0001:
                dir_x = (new_x - cx) / dist
                dir_y = (new_y - cy) / dist
                new_x = cx + dir_x * (sz_radius - radius)
                new_y = cy + dir_y * (sz_radius - radius)
            else:
                new_x = cx
                new_y = cy
            bounced = True

        return new_x, new_y, bounced

    def update_zone(self, current_tick: int, delta: float):
        if current_tick != self.last_tick:
            self.last_tick = current_tick
            if self.safe_zone_radius > 50.0:
                self.safe_zone_radius -= 10.0 * delta
                if self.safe_zone_radius <= 50.0:
                    self.safe_zone_radius = 50.0
            else:
                if current_tick % 120 == 0:
                    import random
                    if hasattr(self, "_trigger_event"):
                        self._trigger_event(random.choice(["meteor_shower", "gravity_shift", "orbital_strike", "anomaly_zone", "massive_black_hole_event"]), current_tick)
                    else:
                        event_type = random.choice(["meteor_shower", "gravity_shift", "anomaly_zone", "massive_black_hole_event"])
                        if event_type == "meteor_shower":
                            for _ in range(10):
                                x = random.uniform(50, self.width - 50)
                                y = random.uniform(50, self.height - 50)
                                # Assuming Hazard is imported in basic_arena

                                m = Hazard(id=len(self.hazards) + random.randint(1000, 9999), x=x, y=y, radius=30.0, kind="meteor", damage=200.0)
                                m.target_radius = 30.0
                                setattr(m, "duration", 5.0)
                                self.hazards.append(m)
                        elif event_type == "massive_black_hole_event":
                            h_id = 9000 + len(self.hazards)
                            mbh = Hazard(id=h_id, x=self.width/2, y=self.height/2, radius=100.0, kind="massive_black_hole", damage=10.0)
                            mbh.target_radius = 500.0
                            setattr(mbh, "duration", 20.0)
                            setattr(mbh, "pull_strength", 100.0)
                            self.hazards.append(mbh)
                        elif event_type == "anomaly_zone":
                            zone = Hazard(id=len(self.hazards) + random.randint(3000, 9999), x=self.width/2, y=self.height/2, radius=self.width/2, kind="anomaly_zone", damage=0.0)
                            setattr(zone, "duration", 10.0)
                            self.hazards.append(zone)
                        elif event_type == "gravity_shift":

                            gw = Hazard(id=len(self.hazards) + random.randint(3000, 9999), x=self.width/2, y=self.height/2, radius=self.width/2, kind="gravity_well", damage=10.0)
                            setattr(gw, "duration", 10.0)
                            self.hazards.append(gw)

            for h in self.hazards:
                if hasattr(h, "target_radius"):
                    if h.radius < h.target_radius:
                        h.radius += (h.target_radius / 600.0) * delta * 60.0
                        if h.radius > h.target_radius:
                            h.radius = h.target_radius

        if current_tick % 600 == 0:
            import random
            self.hazards = []
            num_zones = random.randint(1, 3)
            for _ in range(num_zones):
                x = random.uniform(200, self.width - 200)
                y = random.uniform(200, self.height - 200)
                t_radius = random.uniform(100.0, 250.0)
                new_hazard = Hazard(id=len(self.hazards), x=x, y=y, radius=10.0, kind="trap", damage=100.0)
                new_hazard.target_radius = t_radius
                self.hazards.append(new_hazard)

        if current_tick % 10 == 0:
            self._update_danger_grid()

    def _update_danger_grid(self):
        self.danger_grid.clear()

        # Check hazards
        for h in self.hazards:
            grid_x = int(h.x // 100)
            grid_y = int(h.y // 100)
            r_cells = int(h.radius // 100) + 1
            for i in range(grid_x - r_cells, grid_x + r_cells + 1):
                for j in range(grid_y - r_cells, grid_y + r_cells + 1):
                    cx = i * 100 + 50
                    cy = j * 100 + 50
                    dist = ((cx - h.x)**2 + (cy - h.y)**2)**0.5
                    if dist <= h.radius + 50:
                        self.danger_grid[(i, j)] = self.danger_grid.get((i, j), 0.0) + (h.damage / 10.0)

        # Check safe zone
        grid_w = int(self.width // 100) + 1
        grid_h = int(self.height // 100) + 1
        for i in range(grid_w):
            for j in range(grid_h):
                cx = i * 100 + 50
                cy = j * 100 + 50
                dist_to_center = ((cx - self.safe_zone_center[0])**2 + (cy - self.safe_zone_center[1])**2)**0.5
                if dist_to_center > self.safe_zone_radius:
                    self.danger_grid[(i, j)] = self.danger_grid.get((i, j), 0.0) + 5.0