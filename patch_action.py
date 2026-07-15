with open("src/ai/action.py", "r") as f:
    text = f.read()

text = text.replace("pull_strength = (hazard.radius * 2.0 * radius_mult / max(10.0, dist)) * 200.0 * delta\n                            nx, ny", "pull_strength = (hazard.radius * 2.0 * radius_mult / max(10.0, dist)) * 200.0 * delta\n                            if getattr(self.world, 'is_gravity_reversed', False): pull_strength *= -1.0\n                            nx, ny")
text = text.replace("pull_strength = (getattr(hazard, \"radius\", 150.0) * 3.0 / max(10.0, dist)) * 80.0 * delta\n                                self.ball.x", "pull_strength = (getattr(hazard, \"radius\", 150.0) * 3.0 / max(10.0, dist)) * 80.0 * delta\n                                if getattr(self.world, 'is_gravity_reversed', False): pull_strength *= -1.0\n                                self.ball.x")
text = text.replace("pull_strength = 200.0 * delta\n                                if isinstance(item, dict):", "pull_strength = 200.0 * delta\n                                if getattr(self.world, 'is_gravity_reversed', False): pull_strength *= -1.0\n                                if isinstance(item, dict):")
text = text.replace("pull_strength = 150.0 * delta\n                                if hasattr(hazard, \"x\"):", "pull_strength = 150.0 * delta\n                                if getattr(self.world, 'is_gravity_reversed', False): pull_strength *= -1.0\n                                if hasattr(hazard, \"x\"):")
text = text.replace("pull_strength = 100.0 * delta\n                                # Weak pull towards the center", "pull_strength = 100.0 * delta\n                                if getattr(self.world, 'is_gravity_reversed', False): pull_strength *= -1.0\n                                # Weak pull towards the center")
text = text.replace("pull_strength = 100.0 * delta\n                                if getattr(self.ball, \"anchor_booster_timer\", 0.0) <= 0:", "pull_strength = 100.0 * delta\n                                if getattr(self.world, 'is_gravity_reversed', False): pull_strength *= -1.0\n                                if getattr(self.ball, \"anchor_booster_timer\", 0.0) <= 0:")
text = text.replace("pull_strength = 300.0 * delta\n                dx = target.x", "pull_strength = 300.0 * delta\n                if getattr(self.world, 'is_gravity_reversed', False): pull_strength *= -1.0\n                dx = target.x")

with open("src/ai/action.py", "w") as f:
    f.write(text)

with open("src/ai/action.gd", "r") as f:
    gd_text = f.read()

gd_text = gd_text.replace("pull_strength = (hazard.radius * 2.0 * radius_mult / max(10.0, dist)) * 200.0 * delta\n\t\t\t\t\t\t\tvar nx = dx / max(0.1, dist)", "pull_strength = (hazard.radius * 2.0 * radius_mult / max(10.0, dist)) * 200.0 * delta\n\t\t\t\t\t\t\tif typeof(self.world) == TYPE_DICTIONARY and self.world.get(\"is_gravity_reversed\", false):\n\t\t\t\t\t\t\t\tpull_strength *= -1.0\n\t\t\t\t\t\t\telif typeof(self.world) != TYPE_DICTIONARY and \"is_gravity_reversed\" in self.world and self.world.is_gravity_reversed:\n\t\t\t\t\t\t\t\tpull_strength *= -1.0\n\t\t\t\t\t\t\tvar nx = dx / max(0.1, dist)")

with open("src/ai/action.gd", "w") as f:
    f.write(gd_text)
