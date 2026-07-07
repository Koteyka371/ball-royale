import re

with open("src/arena/procedural_arena.py", "r") as f:
    content = f.read()

# 1. Modify __init__
init_replacement = """        # Hexagonal tiles setup
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
        self.safe_zone_center = (arena_size / 2, arena_size / 2)"""

content = re.sub(r'        self.safe_zone_radius = arena_size \* 0.7\n        self.safe_zone_center = \(arena_size / 2, arena_size / 2\)', init_replacement, content)

# 2. Modify is_point_inside
is_point_inside_replacement = """    def is_point_inside(self, x: float, y: float, radius: float) -> bool:
        nearest_hex = None
        min_dist = float('inf')
        for t in getattr(self, "hex_tiles", []):
            dist = (x - t["x"])**2 + (y - t["y"])**2
            if dist < min_dist:
                min_dist = dist
                nearest_hex = t

        if nearest_hex and nearest_hex["state"] == "fallen":
            return False

        # Check rooms
        for r in self.rooms:
            if r.x + radius <= x <= r.x + r.width - radius and r.y + radius <= y <= r.y + r.height - radius:
                return True
        # Check corridors
        for c in self.corridors:
            if c.x + radius <= x <= c.x + c.width - radius and c.y + radius <= y <= c.y + c.height - radius:
                return True
        return False"""

content = re.sub(r'    def is_point_inside\(self, x: float, y: float, radius: float\) -> bool:.*?        return False', is_point_inside_replacement, content, flags=re.DOTALL)

# 3. Modify clamp_position to NOT pull inwards for safe zone
clamp_position_replacement = """        return nearest_x, nearest_y, True"""

content = re.sub(r'        import math\n        sz_cx, sz_cy = self.safe_zone_center\n        sz_radius = self.safe_zone_radius\n        dist = math.hypot\(nearest_x - sz_cx, nearest_y - sz_cy\).*?        return nearest_x, nearest_y, True', clamp_position_replacement, content, flags=re.DOTALL)


# 4. Modify update_zone
update_zone_replacement = """    def update_zone(self, current_tick: int, delta: float):
        if current_tick != getattr(self, "last_tick", -1):
            self.last_tick = current_tick

            # Handle Hexagonal Tile falling
            if current_tick % 60 == 0:
                import random
                safe_tiles = [t for t in getattr(self, "hex_tiles", []) if t["state"] == "safe"]
                if safe_tiles:
                    safe_tiles.sort(key=lambda t: (t["x"] - self.width/2)**2 + (t["y"] - self.height/2)**2, reverse=True)
                    num_to_fall = min(len(safe_tiles), random.randint(1, 3))

                    chosen = []
                    if len(safe_tiles) > 0:
                        chosen.append(safe_tiles[0])
                    for _ in range(num_to_fall - 1):
                        if safe_tiles:
                            chosen.append(random.choice(safe_tiles))

                    for t in chosen:
                        if t["state"] == "safe":
                            t["state"] = "glowing"
                            t["timer"] = 3.0

            # Update glowing timers
            for t in getattr(self, "hex_tiles", []):
                if t["state"] == "glowing":
                    t["timer"] -= delta
                    if t["timer"] <= 0:
                        t["state"] = "fallen"

            if self.safe_zone_radius > 0.0:"""

content = re.sub(r'    def update_zone\(self, current_tick: int, delta: float\):\n        if current_tick != getattr\(self, "last_tick", -1\):\n            self.last_tick = current_tick\n            if self.safe_zone_radius > 0.0:', update_zone_replacement, content)

# 5. Modify danger grid
danger_grid_replacement = """        # Check safe zone (hex tiles)
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
                        self.danger_grid[(i, j)] = self.danger_grid.get((i, j), 0.0) + 2.0"""

content = re.sub(r'        # Check safe zone\n        grid_w = int\(self.width // 100\) \+ 1\n        grid_h = int\(self.height // 100\) \+ 1\n        for i in range\(grid_w\):\n            for j in range\(grid_h\):\n                cx = i \* 100 \+ 50\n                cy = j \* 100 \+ 50\n                dist_to_center = \(\(cx - self.safe_zone_center\[0\]\)\*\*2 \+ \(cy - self.safe_zone_center\[1\]\)\*\*2\)\*\*0\.5\n                if dist_to_center > self.safe_zone_radius:\n                    self.danger_grid\[\(i, j\)\] = self.danger_grid.get\(\(i, j\), 0\.0\) \+ 5\.0', danger_grid_replacement, content)


with open("src/arena/procedural_arena.py", "w") as f:
    f.write(content)
