import re
with open("src/arena/procedural_arena.gd", "r") as f:
    code = f.read()

new_code = code.replace(
"""        var r = rng.randf()
        var kind = "spikes"
        if r < 0.25:
            kind = "lava"
        elif r < 0.34:""",
"""        var r = rng.randf()
        var kind = "spikes"
        if r < 0.25:
            kind = "lava"
        elif r < 0.28:
            kind = "ice_patch"
        elif r < 0.34:""")

with open("src/arena/procedural_arena.gd", "w") as f:
    f.write(new_code)
