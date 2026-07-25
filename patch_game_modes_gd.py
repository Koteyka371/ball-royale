import sys

with open("src/ai/game_modes.gd", "r") as f:
    content = f.read()

target = """	func apply_dynamic_traits(world, balls: Array, delta: float) -> void:
"""

new_code = """	func apply_dynamic_traits(world, balls: Array, delta: float) -> void:
		for b in balls:
			var is_alive = true
			if typeof(b) == TYPE_DICTIONARY:
				is_alive = b.get("alive", true)
			else:
				if "alive" in b: is_alive = b.alive
				elif b.has_method("has_meta") and b.has_meta("alive"): is_alive = b.get_meta("alive")

			var traits = []
			if typeof(b) == TYPE_DICTIONARY:
				traits = b.get("traits", [])
			else:
				if "traits" in b: traits = b.traits
				elif b.has_method("has_meta") and b.has_meta("traits"): traits = b.get_meta("traits")

			if is_alive and traits.has("quantum_echo"):
				var timer = 3.0
				if typeof(b) == TYPE_DICTIONARY:
					timer = b.get("quantum_echo_timer", 3.0)
				else:
					if "quantum_echo_timer" in b: timer = b.quantum_echo_timer
					elif b.has_method("has_meta") and b.has_meta("quantum_echo_timer"): timer = b.get_meta("quantum_echo_timer")

				timer -= delta
				if timer <= 0:
					timer = 3.0
					var ghosts = []
					if typeof(b) == TYPE_DICTIONARY:
						ghosts = b.get("quantum_ghosts", [])
					else:
						if "quantum_ghosts" in b: ghosts = b.quantum_ghosts
						elif b.has_method("has_meta") and b.has_meta("quantum_ghosts"): ghosts = b.get_meta("quantum_ghosts")

					var cur_x = 0.0
					var cur_y = 0.0
					var cur_hp = 100.0
					if typeof(b) == TYPE_DICTIONARY:
						cur_x = b.get("x", 0.0)
						cur_y = b.get("y", 0.0)
						cur_hp = b.get("hp", 100.0)
					else:
						if "x" in b: cur_x = b.x
						elif b.has_method("has_meta") and b.has_meta("x"): cur_x = b.get_meta("x")
						if "y" in b: cur_y = b.y
						elif b.has_method("has_meta") and b.has_meta("y"): cur_y = b.get_meta("y")
						if "hp" in b: cur_hp = b.hp
						elif b.has_method("has_meta") and b.has_meta("hp"): cur_hp = b.get_meta("hp")

					ghosts.insert(0, {"x": cur_x, "y": cur_y, "hp": cur_hp})

					if typeof(b) == TYPE_DICTIONARY:
						b["quantum_echo_timer"] = timer
						b["quantum_ghosts"] = ghosts
					else:
						if "quantum_echo_timer" in b: b.quantum_echo_timer = timer
						elif b.has_method("set_meta"): b.set_meta("quantum_echo_timer", timer)
						if "quantum_ghosts" in b: b.quantum_ghosts = ghosts
						elif b.has_method("set_meta"): b.set_meta("quantum_ghosts", ghosts)

					if typeof(world) == TYPE_DICTIONARY and world.has("events"):
						world.events.append({"type": "quantum_echo_ghost", "x": cur_x, "y": cur_y})
					elif typeof(world) == TYPE_OBJECT and "events" in world:
						world.events.append({"type": "quantum_echo_ghost", "x": cur_x, "y": cur_y})

"""

content = content.replace(target, new_code, 1)

with open("src/ai/game_modes.gd", "w") as f:
    f.write(content)
