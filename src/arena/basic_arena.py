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

        # Generate quantum teleporters
        num_quantum = max(1, int(self.width // 1000))
        for p in range(num_quantum):
            q1_id = len(self.hazards) + 11000 + p*2
            q2_id = len(self.hazards) + 11000 + p*2 + 1

            q1_x, q1_y = self.get_random_spawn_point(30.0)

            q2_x, q2_y = self.get_random_spawn_point(30.0)
            best_dist = (q1_x - q2_x)**2 + (q1_y - q2_y)**2
            for _ in range(10):
                tx, ty = self.get_random_spawn_point(30.0)
                dist = (q1_x - tx)**2 + (q1_y - ty)**2
                if dist > best_dist:
                    best_dist = dist
                    q2_x, q2_y = tx, ty

            q1 = Hazard(id=q1_id, x=q1_x, y=q1_y, radius=30.0, kind="quantum_teleporter", damage=0.0)
            q1.target_x = q2_x
            q1.target_y = q2_y

            q2 = Hazard(id=q2_id, x=q2_x, y=q2_y, radius=30.0, kind="quantum_teleporter", damage=0.0)
            q2.target_x = q1_x
            q2.target_y = q1_y

            self.hazards.append(q1)
            self.hazards.append(q2)
        self.boundary_states = {"top": "bouncy", "bottom": "bouncy", "left": "bouncy", "right": "bouncy"}
        self.boundary_health = {"top": 2000.0, "bottom": 2000.0, "left": 2000.0, "right": 2000.0}
        self.boundary_offsets = {"top": 0.0, "bottom": 0.0, "left": 0.0, "right": 0.0}

    def get_random_spawn_point(self, radius: float) -> Tuple[float, float]:
        return (self.rng.uniform(radius, self.width - radius),
                self.rng.uniform(radius, self.height - radius))

    def is_point_inside(self, x: float, y: float, radius: float) -> bool:
        offsets = getattr(self, "boundary_offsets", {"top": 0.0, "bottom": 0.0, "left": 0.0, "right": 0.0})
        left_bound = radius + offsets.get("left", 0.0)
        right_bound = self.width - radius - offsets.get("right", 0.0)
        top_bound = radius + offsets.get("top", 0.0)
        bottom_bound = self.height - radius - offsets.get("bottom", 0.0)

        if not (left_bound <= x <= right_bound and top_bound <= y <= bottom_bound):
            return False

        import math
        cx, cy = self.safe_zone_center
        sz_radius = self.safe_zone_radius
        dist = math.hypot(x - cx, y - cy)
        return dist <= max(0.0, sz_radius - radius)

    def clamp_position(self, x: float, y: float, radius: float) -> Tuple[float, float, bool]:
        bounced = False
        new_x = x
        new_y = y

        offsets = getattr(self, "boundary_offsets", {"top": 0.0, "bottom": 0.0, "left": 0.0, "right": 0.0})
        left_bound = radius + offsets.get("left", 0.0)
        right_bound = self.width - radius - offsets.get("right", 0.0)
        top_bound = radius + offsets.get("top", 0.0)
        bottom_bound = self.height - radius - offsets.get("bottom", 0.0)

        if x < left_bound:
            new_x = left_bound
            bounced = True
        elif x > right_bound:
            new_x = right_bound
            bounced = True

        if y < top_bound:
            new_y = top_bound
            bounced = True
        elif y > bottom_bound:
            new_y = bottom_bound
            bounced = True

        import math
        cx, cy = self.safe_zone_center
        sz_radius = self.safe_zone_radius
        dist = math.hypot(new_x - cx, new_y - cy)

        # If outside the safe zone, push inwards towards safe zone edge
        if dist > max(0.0, sz_radius - radius):
            if dist > 0.0001:
                dir_x = (new_x - cx) / dist
                dir_y = (new_y - cy) / dist
                new_x = cx + dir_x * max(0.0, sz_radius - radius)
                new_y = cy + dir_y * max(0.0, sz_radius - radius)
            else:
                new_x = cx
                new_y = cy
            bounced = True

        return new_x, new_y, bounced

    def update_zone(self, current_tick: int, delta: float):
        if current_tick != self.last_tick:
            self.last_tick = current_tick
            if self.safe_zone_radius > 0.0:
                self.safe_zone_radius -= 10.0 * delta
                if self.safe_zone_radius <= 0.0:
                    self.safe_zone_radius = 0.0

                # Black hole spawning and merging when safe zone is very small
                if self.safe_zone_radius <= 100.0:
                    import random
                    import math
                    # Spawn new black holes occasionally
                    if current_tick % 60 == 0 and random.random() < 0.5:
                        angle = random.uniform(0, math.pi * 2)
                        dist = random.uniform(0, max(1.0, self.safe_zone_radius))
                        cx = self.width / 2
                        cy = self.height / 2
                        hx = cx + math.cos(angle) * dist
                        hy = cy + math.sin(angle) * dist
                        bh_id = 20000 + len(getattr(self, "hazards", [])) + random.randint(0, 1000)

                        bh = Hazard(id=bh_id, x=hx, y=hy, radius=20.0, kind="black_hole", damage=15.0)
                        bh.duration = 1000.0 # Effectively infinite
                        if not hasattr(self, "hazards"):
                            self.hazards = []
                        self.hazards.append(bh)

                    # Pull all black holes towards the center and merge them
                    bhs = [h for h in getattr(self, "hazards", []) if getattr(h, "kind", "") == "black_hole"]
                    cx = self.width / 2
                    cy = self.height / 2
                    for h in bhs:
                        dx = cx - h.x
                        dy = cy - h.y
                        dist = math.sqrt(dx*dx + dy*dy)
                        if dist > 0.0001:
                            h.x += (dx/dist) * 10.0 * delta
                            h.y += (dy/dist) * 10.0 * delta

                        # Merge logic
                        for other in bhs:
                            if h.id != other.id and getattr(other, "duration", 1.0) > 0.0 and getattr(h, "duration", 1.0) > 0.0:
                                ddx = other.x - h.x
                                ddy = other.y - h.y
                                ddist2 = ddx*ddx + ddy*ddy
                                if ddist2 < (getattr(h, "radius", 20.0) + getattr(other, "radius", 20.0))**2 * 0.25:
                                    # Merge other into h
                                    h.radius = min(150.0, getattr(h, "radius", 20.0) + getattr(other, "radius", 20.0) * 0.5)
                                    h.damage = getattr(h, "damage", 15.0) + getattr(other, "damage", 15.0) * 0.2
                                    other.duration = 0.0 # Mark for destruction
            else:
                if current_tick % 120 == 0:
                    import random
                    if hasattr(self, "_trigger_event"):
                        self._trigger_event(random.choice(["meteor_shower", "gravity_shift", "orbital_strike", "emp_strike", "anomaly_zone", "massive_black_hole_event"]), current_tick)
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
            self.hazards = [h for h in self.hazards if getattr(h, "kind", "") == "quantum_teleporter"]
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