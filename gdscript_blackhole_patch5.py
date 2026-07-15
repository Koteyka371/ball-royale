with open("src/ai/game_modes.gd", "r") as f:
    text = f.read()

# Replace BlackHoleMode
text = text.replace(
"""				# Cap max pull to avoid crazy speeds, but scale the cap too
				pull_strength = min(pull_strength, 150.0 * radius_multiplier)

				if typeof(b) == TYPE_DICTIONARY:""",
"""				# Cap max pull to avoid crazy speeds, but scale the cap too
				pull_strength = min(pull_strength, 150.0 * radius_multiplier)
				var is_rev = false
				if typeof(world) == TYPE_DICTIONARY:
					is_rev = world.get("is_gravity_reversed", false)
				else:
					is_rev = world.is_gravity_reversed if "is_gravity_reversed" in world else false
				if is_rev: pull_strength *= -1.0

				if typeof(b) == TYPE_DICTIONARY:"""
)

with open("src/ai/game_modes.gd", "w") as f:
    f.write(text)
