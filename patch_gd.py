with open("src/arena/procedural_arena.gd", "r") as f:
    content = f.read()
import re
old = """        elif kind == "magnet":
            radius = rng.randf_range(25.0, 45.0)
            damage = 0.0
            var new_hazard = ProceduralArena.Hazard.new(i, spawn_pt[0], spawn_pt[1], radius, kind, damage)
            new_hazard.set_meta("polarity", 1 if rng.randf() > 0.5 else -1)
            hazards.append(new_hazard)
            continue"""
new = """        elif kind == "magnet":
            radius = rng.randf_range(25.0, 45.0)
            damage = 0.0
            var new_hazard = ProceduralArena.Hazard.new(i, spawn_pt[0], spawn_pt[1], radius, kind, damage)
            new_hazard.set_meta("polarity", 1 if rng.randf() > 0.5 else -1)
            hazards.append(new_hazard)
            continue
        elif kind == "shrinking_zone":
            radius = rng.randf_range(100.0, 200.0)
            damage = 15.0
            var new_hazard = ProceduralArena.Hazard.new(i, spawn_pt[0], spawn_pt[1], radius, kind, damage)
            new_hazard.set_meta("shrink_rate", randf_range(2.0, 10.0))
            new_hazard.set_meta("min_radius", randf_range(20.0, 50.0))
            hazards.append(new_hazard)
            continue"""
content = content.replace(old, new)
with open("src/arena/procedural_arena.gd", "w") as f:
    f.write(content)
