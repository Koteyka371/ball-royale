with open("src/ai/game_modes.gd", "r") as f:
    text = f.read()

import re
text = re.sub(
    r'(pull_strength = min\(pull_strength, 150\.0 \* radius_multiplier\))\n(\s+if typeof\(b\) == TYPE_DICTIONARY:)',
    r'\1\n\t\t\t\tvar is_rev = false\n\t\t\t\tif typeof(world) == TYPE_DICTIONARY:\n\t\t\t\t\tis_rev = world.get("is_gravity_reversed", false)\n\t\t\t\telse:\n\t\t\t\t\tis_rev = world.is_gravity_reversed if "is_gravity_reversed" in world else false\n\t\t\t\tif is_rev: pull_strength *= -1.0\n\2',
    text
)

text = re.sub(
    r'(var pull_factor = pull_strength / max\(100\.0, dist\))\n(\s+if typeof\(b\) == TYPE_DICTIONARY:\n\s+if not \("vx" in b\): b\["vx"\] = 0\.0\n\s+if not \("vy" in b\): b\["vy"\] = 0\.0\n\s+b\["vx"\] \+= \(dx / dist\) \* )(pull_strength)( \* pull_factor \* delta)',
    r'\1\n\t\t\t\tvar is_rev = false\n\t\t\t\tif typeof(world) == TYPE_DICTIONARY:\n\t\t\t\t\tis_rev = world.get("is_gravity_reversed", false)\n\t\t\t\telse:\n\t\t\t\t\tis_rev = world.is_gravity_reversed if "is_gravity_reversed" in world else false\n\t\t\t\tvar mod_pull = -pull_strength if is_rev else pull_strength\n\2mod_pull\4',
    text
)
# Do the rest by simple replace where appropriate
text = text.replace('b["vy"] += (dy / dist) * pull_strength * pull_factor * delta', 'b["vy"] += (dy / dist) * mod_pull * pull_factor * delta')
text = text.replace('b.vx += (dx / dist) * pull_strength * pull_factor * delta', 'b.vx += (dx / dist) * mod_pull * pull_factor * delta')
text = text.replace('b.vy += (dy / dist) * pull_strength * pull_factor * delta', 'b.vy += (dy / dist) * mod_pull * pull_factor * delta')

with open("src/ai/game_modes.gd", "w") as f:
    f.write(text)
