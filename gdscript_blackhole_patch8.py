with open("src/ai/game_modes.gd", "r") as f:
    text = f.read()

import re

# MassiveBlackHoleEventMode also has a pull cap
text = re.sub(
    r'(pull_strength = min\(pull_strength, 150\.0 \* radius_multiplier\))\n\t\t\t\t\t\n\t\t\t\t\tif typeof\(b\) == TYPE_DICTIONARY:\n\t\t\t\t\t\tb\["x"\] \+= \(dx / dist\) \* pull_strength \* delta',
    r'\1\n\t\t\t\t\tvar is_rev = false\n\t\t\t\t\tif typeof(world) == TYPE_DICTIONARY:\n\t\t\t\t\t\tis_rev = world.get("is_gravity_reversed", false)\n\t\t\t\t\telse:\n\t\t\t\t\t\tis_rev = world.is_gravity_reversed if "is_gravity_reversed" in world else false\n\t\t\t\t\tif is_rev: pull_strength *= -1.0\n\n\t\t\t\t\tif typeof(b) == TYPE_DICTIONARY:\n\t\t\t\t\t\tb["x"] += (dx / dist) * pull_strength * delta',
    text
)

text = re.sub(
    r'(var pull_factor = pull_strength / max\(100\.0, dist\))\n\n\t\t\t\t\tif typeof\(b\) == TYPE_DICTIONARY:\n\t\t\t\t\t\tif not \("vx" in b\): b\["vx"\] = 0\.0\n\t\t\t\t\t\tif not \("vy" in b\): b\["vy"\] = 0\.0\n\t\t\t\t\t\tb\["vx"\] \+= \(dx / dist\) \* (pull_strength) \* pull_factor \* delta',
    r'\1\n\t\t\t\t\tvar is_rev = false\n\t\t\t\t\tif typeof(world) == TYPE_DICTIONARY:\n\t\t\t\t\t\tis_rev = world.get("is_gravity_reversed", false)\n\t\t\t\t\telse:\n\t\t\t\t\t\tis_rev = world.is_gravity_reversed if "is_gravity_reversed" in world else false\n\t\t\t\t\tvar mod_pull = -pull_strength if is_rev else pull_strength\n\n\t\t\t\t\tif typeof(b) == TYPE_DICTIONARY:\n\t\t\t\t\t\tif not ("vx" in b): b["vx"] = 0.0\n\t\t\t\t\t\tif not ("vy" in b): b["vy"] = 0.0\n\t\t\t\t\t\tb["vx"] += (dx / dist) * mod_pull * pull_factor * delta',
    text
)

with open("src/ai/game_modes.gd", "w") as f:
    f.write(text)
