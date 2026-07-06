import re

with open("src/arena/procedural_arena.py", "r") as f:
    content = f.read()

# Fix the trailing '\)'
content = content.replace(
    'singularity", "ice_patches"]\\)',
    'singularity", "ice_patches"])'
)

with open("src/arena/procedural_arena.py", "w") as f:
    f.write(content)
