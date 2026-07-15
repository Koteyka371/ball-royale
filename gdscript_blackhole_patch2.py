import re
with open("src/ai/game_modes.gd", "r") as f:
    text = f.read()

# Try again with a less strict replacement string
text = re.sub(
    r'(pull_strength = min\(pull_strength, 150\.0 \* radius_multiplier\))(\s+if typeof\(b\) == TYPE_DICTIONARY:)',
    r'\1\n\t\t\t\tvar is_rev = false\n\t\t\t\tif typeof(world) == TYPE_DICTIONARY:\n\t\t\t\t\tis_rev = world.get("is_gravity_reversed", false)\n\t\t\t\telse:\n\t\t\t\t\tis_rev = world.is_gravity_reversed if "is_gravity_reversed" in world else false\n\t\t\t\tif is_rev: pull_strength *= -1.0\2',
    text
)

text = re.sub(
    r'(var pull_factor = pull_strength / max\(100\.0, dist\))(\s+if typeof\(b\) == TYPE_DICTIONARY:)',
    r'\1\n\t\t\t\tvar is_rev = false\n\t\t\t\tif typeof(world) == TYPE_DICTIONARY:\n\t\t\t\t\tis_rev = world.get("is_gravity_reversed", false)\n\t\t\t\telse:\n\t\t\t\t\tis_rev = world.is_gravity_reversed if "is_gravity_reversed" in world else false\n\t\t\t\tvar mod_pull = -pull_strength if is_rev else pull_strength\2',
    text
)
# And replace pull_strength with mod_pull in the subsequent lines (CenterBlackHoleMode and MassiveBlackHoleEventMode)
# Actually, I'll just replace the specific lines
text = text.replace('b["vx"] += (dx / dist) * pull_strength * pull_factor * delta', 'b["vx"] += (dx / dist) * mod_pull * pull_factor * delta')
text = text.replace('b["vy"] += (dy / dist) * pull_strength * pull_factor * delta', 'b["vy"] += (dy / dist) * mod_pull * pull_factor * delta')
text = text.replace('b.vx += (dx / dist) * pull_strength * pull_factor * delta', 'b.vx += (dx / dist) * mod_pull * pull_factor * delta')
text = text.replace('b.vy += (dy / dist) * pull_strength * pull_factor * delta', 'b.vy += (dy / dist) * mod_pull * pull_factor * delta')

with open("src/ai/game_modes.gd", "w") as f:
    f.write(text)
