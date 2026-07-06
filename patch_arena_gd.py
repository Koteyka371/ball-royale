import re

with open("src/arena/procedural_arena.gd", "r") as f:
    content = f.read()

# Add probability logic
replacement1 = r"""        elif r < 0.99982:
            kind = "frictionless_zone"
        elif r < 0.99983:
            kind = "ice_patches\""""

content = re.sub(
    r'        elif r < 0\.99982:\n            kind = "frictionless_zone"',
    replacement1,
    content
)

# Add initialization logic
replacement2 = r"""        elif kind == "frictionless_zone":
            radius = rng.randf_range(40.0, 80.0)
            damage = 0.0
        elif kind == "ice_patches":
            radius = rng.randf_range(30.0, 60.0)
            damage = 0.0"""

content = re.sub(
    r'        elif kind == "frictionless_zone":\n            radius = rng\.randf_range\(40\.0, 80\.0\)\n            damage = 0\.0',
    replacement2,
    content
)

with open("src/arena/procedural_arena.gd", "w") as f:
    f.write(content)
