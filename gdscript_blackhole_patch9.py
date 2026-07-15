with open("src/ai/game_modes.gd", "r") as f:
    text = f.read()

import re

# BlackHoleMode
text = re.sub(
    r'(var pull_strength = \d+\.\d+ / \(dist \* dist\)\n\n\t\t\t\t# Increase max pull and overall strength as the black hole grows\n\t\t\t\tvar radius_multiplier = black_hole_radius / 50\.0\n\t\t\t\tpull_strength \*= radius_multiplier\n\n\t\t\t\t# Cap max pull to avoid crazy speeds, but scale the cap too\n\t\t\t\tpull_strength = min\(pull_strength, 150\.0 \* radius_multiplier\))\n\n\t\t\t\tif typeof\(b\) == TYPE_DICTIONARY:',
    r'\1\n\t\t\t\tvar is_rev = false\n\t\t\t\tif typeof(world) == TYPE_DICTIONARY:\n\t\t\t\t\tis_rev = world.get("is_gravity_reversed", false)\n\t\t\t\telse:\n\t\t\t\t\tis_rev = world.is_gravity_reversed if "is_gravity_reversed" in world else false\n\t\t\t\tif is_rev: pull_strength *= -1.0\n\n\t\t\t\tif typeof(b) == TYPE_DICTIONARY:',
    text
)

# CenterBlackHoleMode
text = text.replace(
    'var pull_x = (dx / dist) * pull_strength * delta',
    'var is_rev = false\n\t\t\t\tif typeof(world) == TYPE_DICTIONARY:\n\t\t\t\t\tis_rev = world.get("is_gravity_reversed", false)\n\t\t\t\telse:\n\t\t\t\t\tis_rev = world.is_gravity_reversed if "is_gravity_reversed" in world else false\n\t\t\t\tvar mod_pull = -pull_strength if is_rev else pull_strength\n\t\t\t\tvar pull_x = (dx / dist) * mod_pull * delta'
)
text = text.replace(
    'var pull_y = (dy / dist) * pull_strength * delta',
    'var pull_y = (dy / dist) * mod_pull * delta'
)

# MassiveBlackHoleEventMode
text = re.sub(
    r'(var pull_factor = pull_strength / max\(100\.0, dist\))\n\n\t\t\t\tif typeof\(b\) == TYPE_DICTIONARY:\n\t\t\t\t\tif not \("vx" in b\): b\["vx"\] = 0\.0\n\t\t\t\t\tif not \("vy" in b\): b\["vy"\] = 0\.0\n\t\t\t\t\tb\["vx"\] \+= \(dx / dist\) \* pull_strength \* pull_factor \* delta\n\t\t\t\t\tb\["vy"\] \+= \(dy / dist\) \* pull_strength \* pull_factor \* delta\n\t\t\t\telse:\n\t\t\t\t\tif not \("vx" in b\): b\.vx = 0\.0\n\t\t\t\t\tif not \("vy" in b\): b\.vy = 0\.0\n\t\t\t\t\tb\.vx \+= \(dx / dist\) \* pull_strength \* pull_factor \* delta\n\t\t\t\t\tb\.vy \+= \(dy / dist\) \* pull_strength \* pull_factor \* delta',
    r'\1\n\t\t\t\tvar is_rev = false\n\t\t\t\tif typeof(world) == TYPE_DICTIONARY:\n\t\t\t\t\tis_rev = world.get("is_gravity_reversed", false)\n\t\t\t\telse:\n\t\t\t\t\tis_rev = world.is_gravity_reversed if "is_gravity_reversed" in world else false\n\t\t\t\tvar mod_pull = -pull_strength if is_rev else pull_strength\n\n\t\t\t\tif typeof(b) == TYPE_DICTIONARY:\n\t\t\t\t\tif not ("vx" in b): b["vx"] = 0.0\n\t\t\t\t\tif not ("vy" in b): b["vy"] = 0.0\n\t\t\t\t\tb["vx"] += (dx / dist) * mod_pull * pull_factor * delta\n\t\t\t\t\tb["vy"] += (dy / dist) * mod_pull * pull_factor * delta\n\t\t\t\telse:\n\t\t\t\t\tif not ("vx" in b): b.vx = 0.0\n\t\t\t\t\tif not ("vy" in b): b.vy = 0.0\n\t\t\t\t\tb.vx += (dx / dist) * mod_pull * pull_factor * delta\n\t\t\t\t\tb.vy += (dy / dist) * mod_pull * pull_factor * delta',
    text
)


with open("src/ai/game_modes.gd", "w") as f:
    f.write(text)
