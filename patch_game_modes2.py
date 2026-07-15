with open("src/ai/game_modes.py", "r") as f:
    text = f.read()

text = text.replace("pull_strength = min(pull_strength, 150.0 * radius_multiplier)\n\n                    b.x", "pull_strength = min(pull_strength, 150.0 * radius_multiplier)\n                    if getattr(world, 'is_gravity_reversed', False): pull_strength *= -1.0\n\n                    b.x")
text = text.replace("b.vx += (dx / dist) * self.pull_strength * delta", "mod_pull = -self.pull_strength if getattr(world, 'is_gravity_reversed', False) else self.pull_strength\n                    b.vx += (dx / dist) * mod_pull * delta")
text = text.replace("b.vy += (dy / dist) * self.pull_strength * delta", "b.vy += (dy / dist) * mod_pull * delta")
text = text.replace("push_strength = 2000.0 * (1.0 - min(1.0, dist / self.max_danger_radius)) # Stronger push closer to center\n                    if not hasattr(b, \"vx\"):", "push_strength = 2000.0 * (1.0 - min(1.0, dist / self.max_danger_radius))\n                    if getattr(world, 'is_gravity_reversed', False): push_strength *= -1.0\n                    if not hasattr(b, \"vx\"):")

with open("src/ai/game_modes.py", "w") as f:
    f.write(text)

with open("src/ai/game_modes.gd", "r") as f:
    gd_text = f.read()

gd_text = gd_text.replace("pull_strength = min(pull_strength, 150.0 * radius_multiplier)\n\n\t\t\t\t\tif typeof(b) == TYPE_DICTIONARY:", "pull_strength = min(pull_strength, 150.0 * radius_multiplier)\n\t\t\t\t\tvar is_rev = false\n\t\t\t\t\tif typeof(world) == TYPE_DICTIONARY:\n\t\t\t\t\t\tis_rev = world.get(\"is_gravity_reversed\", false)\n\t\t\t\t\telse:\n\t\t\t\t\t\tis_rev = world.is_gravity_reversed if \"is_gravity_reversed\" in world else false\n\t\t\t\t\tif is_rev: pull_strength *= -1.0\n\n\t\t\t\t\tif typeof(b) == TYPE_DICTIONARY:")
gd_text = gd_text.replace("push_strength = 2000.0 * (1.0 - min(1.0, dist / max_danger_radius))\n\t\t\t\t\tif typeof(b) == TYPE_DICTIONARY:", "push_strength = 2000.0 * (1.0 - min(1.0, dist / max_danger_radius))\n\t\t\t\t\tvar is_rev = false\n\t\t\t\t\tif typeof(world) == TYPE_DICTIONARY:\n\t\t\t\t\t\tis_rev = world.get(\"is_gravity_reversed\", false)\n\t\t\t\t\telse:\n\t\t\t\t\t\tis_rev = world.is_gravity_reversed if \"is_gravity_reversed\" in world else false\n\t\t\t\t\tif is_rev: push_strength *= -1.0\n\t\t\t\t\tif typeof(b) == TYPE_DICTIONARY:")

with open("src/ai/game_modes.gd", "w") as f:
    f.write(gd_text)
