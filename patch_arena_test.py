import re
with open("src/arena/test_procedural_arena.py", "r") as f:
    code = f.read()

new_code = code.replace(
"""assert hazard.kind in [""",
"""assert hazard.kind in ["ice_patch", """)

with open("src/arena/test_procedural_arena.py", "w") as f:
    f.write(new_code)
