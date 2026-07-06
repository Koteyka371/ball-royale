import re

with open("src/arena/procedural_arena.gd", "r") as f:
    content = f.read()

# Fix the trailing slash quote issue
content = content.replace(
    'kind = "ice_patches\\"',
    'kind = "ice_patches"'
)

with open("src/arena/procedural_arena.gd", "w") as f:
    f.write(content)
