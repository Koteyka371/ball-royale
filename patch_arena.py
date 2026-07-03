with open("src/arena/procedural_arena.py", "r") as f:
    content = f.read()

target = """        # Shrinking zone
        self.safe_zone_radius = arena_size * 0.7"""

replacement = """        self.terrain_type = random.choice(["grass", "dirt", "sand", "stone", "ice", "metal"])
        # Shrinking zone
        self.safe_zone_radius = arena_size * 0.7"""

content = content.replace(target, replacement)
with open("src/arena/procedural_arena.py", "w") as f:
    f.write(content)
