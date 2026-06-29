with open('src/arena/procedural_arena.gd', 'r') as f:
    content = f.read()

target = """            var event_types = ["meteor_shower", "gravity_shift", "moving_walls", "none"]"""
replacement = """            var event_types = ["meteor_shower", "gravity_shift", "moving_walls", "orbital_strike", "none"]"""

content = content.replace(target, replacement)

with open('src/arena/procedural_arena.gd', 'w') as f:
    f.write(content)
