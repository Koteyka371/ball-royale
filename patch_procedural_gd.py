import re

with open("src/arena/procedural_arena.gd", "r") as f:
    content = f.read()

# 1. Modify _init
init_replacement = """    # Hexagonal tiles setup
    self.set_meta("hex_tiles", [])
    self.set_meta("hex_radius", 120.0)
    var hex_radius = 120.0
    var row_height = 1.5 * hex_radius
    var col_width = sqrt(3.0) * hex_radius

    var rows = int(height / row_height) + 2
    var cols = int(width / col_width) + 2

    var h_tiles = []
    for r in range(rows):
        for c in range(cols):
            var cx = c * col_width
            if r % 2 == 1:
                cx += col_width / 2.0
            var cy = r * row_height

            if -hex_radius <= cx and cx <= width + hex_radius and -hex_radius <= cy and cy <= height + hex_radius:
                var t = {"x": cx, "y": cy, "state": "safe", "timer": 0.0, "radius": hex_radius}
                h_tiles.append(t)
    self.set_meta("hex_tiles", h_tiles)

    safe_zone_radius = width * 0.7
    safe_zone_center = [width / 2.0, height / 2.0]"""

content = re.sub(r'    safe_zone_radius = width \* 0\.7\n    safe_zone_center = \[width / 2\.0, height / 2\.0\]', init_replacement, content)

# 2. Modify is_point_inside
is_point_inside_replacement = """func is_point_inside(x: float, y: float, radius: float) -> bool:
    if self.has_meta("hex_tiles"):
        var h_tiles = self.get_meta("hex_tiles")
        var nearest_hex = null
        var min_dist = 999999999.0
        for t in h_tiles:
            var dist = (x - t["x"])*(x - t["x"]) + (y - t["y"])*(y - t["y"])
            if dist < min_dist:
                min_dist = dist
                nearest_hex = t

        if nearest_hex != null and nearest_hex["state"] == "fallen":
            return false

    for r in rooms:
        if r["x"] + radius <= x and x <= r["x"] + r["width"] - radius and r["y"] + radius <= y and y <= r["y"] + r["height"] - radius:
            return true
    for c in corridors:
        if c["width"] > c["height"]: # horizontal
            if c["x"] + radius <= x and x <= c["x"] + c["width"] - radius and c["y"] + radius <= y and y <= c["y"] + c["height"] - radius:
                return true
        else:
            if c["y"] + radius <= y and y <= c["y"] + c["height"] - radius and c["x"] - c["width"] / 2 + radius <= x and x <= c["x"] + c["width"] / 2 - radius:
                return true
    return false"""

content = re.sub(r'func is_point_inside\(x: float, y: float, radius: float\) -> bool:.*?    return false', is_point_inside_replacement, content, flags=re.DOTALL)


# 3. Modify clamp_position
clamp_position_replacement = """    return [nearest_x, nearest_y, true]"""

content = re.sub(r'    var sz_cx = safe_zone_center\[0\]\n    var sz_cy = safe_zone_center\[1\]\n    var sz_dist = sqrt\(\(nearest_x - sz_cx\)\*\(nearest_x - sz_cx\) \+ \(nearest_y - sz_cy\)\*\(nearest_y - sz_cy\)\).*?    return \[nearest_x, nearest_y, true\]', clamp_position_replacement, content, flags=re.DOTALL)


# 4. Modify update_zone
update_zone_replacement = """func update_zone(current_tick: int, delta: float) -> void:
    if current_tick != last_tick:
        last_tick = current_tick

        # Handle Hexagonal Tile falling
        if current_tick % 60 == 0 and self.has_meta("hex_tiles"):
            var h_tiles = self.get_meta("hex_tiles")
            var safe_tiles = []
            for t in h_tiles:
                if t["state"] == "safe":
                    safe_tiles.append(t)

            if safe_tiles.size() > 0:
                # Sort manually by distance to center
                var cx = width / 2.0
                var cy = height / 2.0
                for i in range(safe_tiles.size()):
                    for j in range(i + 1, safe_tiles.size()):
                        var dist_i = (safe_tiles[i]["x"] - cx)*(safe_tiles[i]["x"] - cx) + (safe_tiles[i]["y"] - cy)*(safe_tiles[i]["y"] - cy)
                        var dist_j = (safe_tiles[j]["x"] - cx)*(safe_tiles[j]["x"] - cx) + (safe_tiles[j]["y"] - cy)*(safe_tiles[j]["y"] - cy)
                        if dist_j > dist_i:
                            var temp = safe_tiles[i]
                            safe_tiles[i] = safe_tiles[j]
                            safe_tiles[j] = temp

                var num_to_fall = min(safe_tiles.size(), (randi() % 3) + 1)
                var chosen = []
                if safe_tiles.size() > 0:
                    chosen.append(safe_tiles[0])
                for i in range(num_to_fall - 1):
                    if safe_tiles.size() > 0:
                        chosen.append(safe_tiles[randi() % safe_tiles.size()])

                for t in chosen:
                    if t["state"] == "safe":
                        t["state"] = "glowing"
                        t["timer"] = 3.0

        if self.has_meta("hex_tiles"):
            var h_tiles = self.get_meta("hex_tiles")
            for t in h_tiles:
                if t["state"] == "glowing":
                    t["timer"] -= delta
                    if t["timer"] <= 0:
                        t["state"] = "fallen"

        if safe_zone_radius > 0.0:"""

content = re.sub(r'func update_zone\(current_tick: int, delta: float\) -> void:\n    if current_tick != last_tick:\n        last_tick = current_tick\n        if safe_zone_radius > 0.0:', update_zone_replacement, content)


# 5. Danger grid
danger_grid_replacement = """    # Check hex tiles for danger
    var grid_w = int(width / 100) + 1
    var grid_h = int(height / 100) + 1
    var h_tiles = []
    if self.has_meta("hex_tiles"):
        h_tiles = self.get_meta("hex_tiles")

    for i in range(grid_w):
        for j in range(grid_h):
            var cx = i * 100 + 50
            var cy = j * 100 + 50
            var nearest_hex = null
            var min_dist = 999999999.0
            for t in h_tiles:
                var dist = (cx - t["x"])*(cx - t["x"]) + (cy - t["y"])*(cy - t["y"])
                if dist < min_dist:
                    min_dist = dist
                    nearest_hex = t

            if nearest_hex != null:
                if nearest_hex["state"] == "fallen":
                    var key = str(i) + "," + str(j)
                    var current = 0.0
                    if danger_grid.has(key):
                        current = danger_grid[key]
                    danger_grid[key] = current + 10.0
                elif nearest_hex["state"] == "glowing":
                    var key = str(i) + "," + str(j)
                    var current = 0.0
                    if danger_grid.has(key):
                        current = danger_grid[key]
                    danger_grid[key] = current + 2.0"""

content = re.sub(r'    var grid_w = int\(width / 100\) \+ 1\n    var grid_h = int\(height / 100\) \+ 1\n    for i in range\(grid_w\):\n        for j in range\(grid_h\):\n            var cx = i \* 100 \+ 50\n            var cy = j \* 100 \+ 50\n            var dist_to_center = sqrt\(\(cx - safe_zone_center\[0\]\)\*\(cx - safe_zone_center\[0\]\) \+ \(cy - safe_zone_center\[1\]\)\*\(cy - safe_zone_center\[1\]\)\)\n            if dist_to_center > safe_zone_radius:\n                var key = str\(i\) \+ "," \+ str\(j\)\n                var current = 0\.0\n                if danger_grid\.has\(key\):\n                    current = danger_grid\[key\]\n                danger_grid\[key\] = current \+ 5\.0', danger_grid_replacement, content)


with open("src/arena/procedural_arena.gd", "w") as f:
    f.write(content)
