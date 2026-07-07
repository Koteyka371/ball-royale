from arena.procedural_arena import Hazard

import random

from typing import Tuple

class BasicArena:
    def __init__(self, arena_size: float = 2000.0, seed: int | None = None):
        self.rng = random.Random(seed)
        self.width = arena_size
        self.height = arena_size

        # Hexagonal tiles setup
        self.hex_tiles = []
        self.hex_radius = 120.0
        row_height = 1.5 * self.hex_radius
        import math
        col_width = math.sqrt(3) * self.hex_radius

        rows = int(self.height / row_height) + 2
        cols = int(self.width / col_width) + 2

        for r in range(rows):
            for c in range(cols):
                cx = c * col_width
                if r % 2 == 1:
                    cx += col_width / 2.0
                cy = r * row_height

                if -self.hex_radius <= cx <= self.width + self.hex_radius and -self.hex_radius <= cy <= self.height + self.hex_radius:
                    self.hex_tiles.append({
                        "x": cx,
                        "y": cy,
                        "state": "safe",
                        "timer": 0.0,
                        "radius": self.hex_radius
                    })

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

    def get_random_spawn_point(self, radius: float) -> Tuple[float, float]:
        return (self.rng.uniform(radius, self.width - radius),
                self.rng.uniform(radius, self.height - radius))

    def is_point_inside(self, x: float, y: float, radius: float) -> bool:
        if not (radius <= x <= self.width - radius and radius <= y <= self.height - radius):
            return False

        nearest_hex = None
        min_dist = float('inf')
        for t in getattr(self, "hex_tiles", []):
            dist = (x - t["x"])**2 + (y - t["y"])**2
            if dist < min_dist:
                min_dist = dist
                nearest_hex = t

        if nearest_hex and nearest_hex["state"] == "fallen":
            return False

        return True

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

            # Handle Hexagonal Tile falling
            if current_tick % 60 == 0:
                import random
                safe_tiles = [t for t in getattr(self, "hex_tiles", []) if t["state"] == "safe"]
                if safe_tiles:
                    # Sort by distance to center descending, to make edge tiles fall more often
                    safe_tiles.sort(key=lambda t: (t["x"] - self.width/2)**2 + (t["y"] - self.height/2)**2, reverse=True)
                    num_to_fall = min(len(safe_tiles), random.randint(1, 3))

                    chosen = []
                    if len(safe_tiles) > 0:
                        chosen.append(safe_tiles[0]) # Always take one from the edge
                    for _ in range(num_to_fall - 1):
                        if safe_tiles:
                            chosen.append(random.choice(safe_tiles))

                    for t in chosen:
                        if t["state"] == "safe":
                            t["state"] = "glowing"
                            t["timer"] = 3.0 # glow red for 3 seconds before falling

            # Update glowing timers
            for t in getattr(self, "hex_tiles", []):
                if t["state"] == "glowing":
                    t["timer"] -= delta
                    if t["timer"] <= 0:
                        t["state"] = "fallen"

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

        # Check safe zone (hex tiles)
        grid_w = int(self.width // 100) + 1
        grid_h = int(self.height // 100) + 1
        for i in range(grid_w):
            for j in range(grid_h):
                cx = i * 100 + 50
                cy = j * 100 + 50
                nearest_hex = None
                min_dist = float('inf')
                for t in getattr(self, "hex_tiles", []):
                    dist = (cx - t["x"])**2 + (cy - t["y"])**2
                    if dist < min_dist:
                        min_dist = dist
                        nearest_hex = t

                if nearest_hex:
                    if nearest_hex["state"] == "fallen":
                        self.danger_grid[(i, j)] = self.danger_grid.get((i, j), 0.0) + 10.0
                    elif nearest_hex["state"] == "glowing":
                        self.danger_grid[(i, j)] = self.danger_grid.get((i, j), 0.0) + 2.0