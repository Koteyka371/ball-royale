with open("src/ai/game_modes.gd", "r") as f:
    text = f.read()

# BlackHoleMode
text = text.replace(
"""				var pull_strength = 20000.0 / (dist * dist)

				# Increase max pull and overall strength as the black hole grows
				var radius_multiplier = black_hole_radius / 50.0
				pull_strength *= radius_multiplier

				# Cap max pull to avoid crazy speeds, but scale the cap too
				pull_strength = min(pull_strength, 150.0 * radius_multiplier)

				if typeof(b) == TYPE_DICTIONARY:""",
"""				var pull_strength = 20000.0 / (dist * dist)

				# Increase max pull and overall strength as the black hole grows
				var radius_multiplier = black_hole_radius / 50.0
				pull_strength *= radius_multiplier

				# Cap max pull to avoid crazy speeds, but scale the cap too
				pull_strength = min(pull_strength, 150.0 * radius_multiplier)
				var is_rev = false
				if typeof(world) == TYPE_DICTIONARY:
					is_rev = world.get("is_gravity_reversed", false)
				else:
					is_rev = world.is_gravity_reversed if "is_gravity_reversed" in world else false
				if is_rev: pull_strength *= -1.0

				if typeof(b) == TYPE_DICTIONARY:"""
)

# CenterBlackHoleMode
text = text.replace(
"""				var pull_factor = pull_strength / max(100.0, dist)

				if typeof(b) == TYPE_DICTIONARY:
					if not ("vx" in b): b["vx"] = 0.0
					if not ("vy" in b): b["vy"] = 0.0
					b["vx"] += (dx / dist) * pull_strength * pull_factor * delta
					b["vy"] += (dy / dist) * pull_strength * pull_factor * delta""",
"""				var pull_factor = pull_strength / max(100.0, dist)
				var is_rev = false
				if typeof(world) == TYPE_DICTIONARY:
					is_rev = world.get("is_gravity_reversed", false)
				else:
					is_rev = world.is_gravity_reversed if "is_gravity_reversed" in world else false
				var mod_pull = -pull_strength if is_rev else pull_strength

				if typeof(b) == TYPE_DICTIONARY:
					if not ("vx" in b): b["vx"] = 0.0
					if not ("vy" in b): b["vy"] = 0.0
					b["vx"] += (dx / dist) * mod_pull * pull_factor * delta
					b["vy"] += (dy / dist) * mod_pull * pull_factor * delta"""
)
text = text.replace(
"""				else:
					if not ("vx" in b): b.vx = 0.0
					if not ("vy" in b): b.vy = 0.0
					b.vx += (dx / dist) * pull_strength * pull_factor * delta
					b.vy += (dy / dist) * pull_strength * pull_factor * delta""",
"""				else:
					if not ("vx" in b): b.vx = 0.0
					if not ("vy" in b): b.vy = 0.0
					b.vx += (dx / dist) * mod_pull * pull_factor * delta
					b.vy += (dy / dist) * mod_pull * pull_factor * delta"""
)

with open("src/ai/game_modes.gd", "w") as f:
    f.write(text)
