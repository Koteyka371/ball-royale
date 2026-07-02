with open("src/arena/procedural_arena.gd", "r") as f:
    content = f.read()

old = """            elif h.kind == "orbital_strike":
                if h.has_meta("duration"):
                    var dur = h.get_meta("duration") - delta
                    if dur <= 0:
                        h.kind = "orbital_strike_active"
                        h.set_meta("duration", 0.5)
                        h.damage = 1000.0
                    else:
                        h.set_meta("duration", dur)"""
new = """            elif h.kind == "orbital_strike":
                if h.has_meta("duration"):
                    var dur = h.get_meta("duration") - delta
                    if dur <= 0:
                        h.kind = "orbital_strike_active"
                        h.set_meta("duration", 0.5)
                        h.damage = 1000.0
                    else:
                        h.set_meta("duration", dur)
            elif h.kind == "shrinking_zone":
                var shrink_rate = 5.0
                var min_radius = 20.0
                if h.has_meta("shrink_rate"): shrink_rate = h.get_meta("shrink_rate")
                if h.has_meta("min_radius"): min_radius = h.get_meta("min_radius")
                if h.radius > min_radius:
                    h.radius -= shrink_rate * delta
                    if h.radius < min_radius:
                        h.radius = min_radius"""

content = content.replace(old, new)
with open("src/arena/procedural_arena.gd", "w") as f:
    f.write(content)
