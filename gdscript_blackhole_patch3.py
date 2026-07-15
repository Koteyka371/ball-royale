with open("src/ai/game_modes.gd", "r") as f:
    text = f.read()

# Just look for pull_strength and push_strength in all modes and replace it if we can find it
import re

text = re.sub(
    r'(var pull_strength = \d+\.\d+ / \(dist \* dist\)\s+var radius_multiplier = black_hole_radius / 50\.0\s+pull_strength \*= radius_multiplier\s+pull_strength = min\(pull_strength, 150\.0 \* radius_multiplier\))(\s+if typeof\(b\) == TYPE_DICTIONARY:)',
    r'\1\n\t\t\t\tvar is_rev = false\n\t\t\t\tif typeof(world) == TYPE_DICTIONARY:\n\t\t\t\t\tis_rev = world.get("is_gravity_reversed", false)\n\t\t\t\telse:\n\t\t\t\t\tis_rev = world.is_gravity_reversed if "is_gravity_reversed" in world else false\n\t\t\t\tif is_rev: pull_strength *= -1.0\2',
    text
)

with open("src/ai/game_modes.gd", "w") as f:
    f.write(text)
