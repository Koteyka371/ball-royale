import re

with open("src/arena/procedural_arena.py", "r") as f:
    content = f.read()

# Add ice_patches to the list of choices
content = re.sub(
    r'(\["spikes", "lava",.*?)"\]\)',
    r'\1", "ice_patches"]\)',
    content
)

# Add the elif block for ice_patches
replacement = r"""            elif kind == "frictionless_zone":
                radius = random.uniform(40.0, 80.0)
                damage = 0.0
            elif kind == "ice_patches":
                radius = random.uniform(30.0, 60.0)
                damage = 0.0"""

content = re.sub(
    r'            elif kind == "frictionless_zone":\n                radius = random.uniform\(40\.0, 80\.0\)\n                damage = 0\.0',
    replacement,
    content
)

with open("src/arena/procedural_arena.py", "w") as f:
    f.write(content)
