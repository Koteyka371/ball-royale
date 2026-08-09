
class ConstrictingArenaMode extends GameMode:
	var min_width = 200.0
	var min_height = 200.0
	var shrink_speed = 10.0
	var damage_per_second = 20.0
	var slow_duration = 1.0

	func _init().():
		name = "Constricting Arena"
		description = "The arena boundaries slowly constrict over time, pushing all balls towards the center. Touching the outer boundary applies a severe slow and damages over time."

	func tick(world, balls: Array, delta: float = 0.016) -> void:
		.tick(world, balls, delta)

		if world != null and ("arena" in world) and world.arena != null:
			var current_w = 1000.0
			var current_h = 1000.0

			if typeof(world.arena) == TYPE_DICTIONARY:
				current_w = world.arena.get("width", 1000.0)
				current_h = world.arena.get("height", 1000.0)
			else:
				if "width" in world.arena: current_w = world.arena.width
				if "height" in world.arena: current_h = world.arena.height

			var new_w = max(min_width, current_w - shrink_speed * delta)
			var new_h = max(min_height, current_h - shrink_speed * delta)

			if typeof(world.arena) == TYPE_DICTIONARY:
				world.arena["width"] = new_w
				world.arena["height"] = new_h
			else:
				world.arena.width = new_w
				world.arena.height = new_h

			for b in balls:
			var is_alive = false
			var b_type = ""

			if typeof(b) == TYPE_OBJECT:
				if "alive" in b: is_alive = b.alive
				elif b.has_method("has_meta") and b.has_meta("alive"): is_alive = b.get_meta("alive")
				if "ball_type" in b: b_type = b.ball_type
				elif b.has_method("has_meta") and b.has_meta("ball_type"): b_type = b.get_meta("ball_type")
			elif typeof(b) == TYPE_DICTIONARY:
				if b.has("alive"): is_alive = b["alive"]
				if b.has("ball_type"): b_type = b["ball_type"]

			if not is_alive or b_type == "spectator":
				continue

			if typeof(b) == TYPE_OBJECT:
				if b.has_method("has_meta") and b.has_meta("quantum_teleport_cooldown"):
					var cd = float(b.get_meta("quantum_teleport_cooldown"))
					cd -= delta
					if cd <= 0:
						b.set_meta("quantum_teleport_cooldown", 0.0)
					else:
						b.set_meta("quantum_teleport_cooldown", cd)

				if b.has_method("has_meta") and b.has_meta("quantum_scramble_timer"):
					var st = float(b.get_meta("quantum_scramble_timer"))
					if st > 0:
						st -= delta
						if st <= 0:
							b.set_meta("quantum_scramble_timer", 0.0)
							if b.has_meta("base_speed_scrambled") and "speed" in b: b.speed = b.get_meta("base_speed_scrambled")
							if b.has_meta("base_radius_scrambled") and "radius" in b: b.radius = b.get_meta("base_radius_scrambled")
							if b.has_meta("base_damage_mult_scrambled") and "damage_multiplier" in b: b.damage_multiplier = b.get_meta("base_damage_mult_scrambled")
						else:
							b.set_meta("quantum_scramble_timer", st)
			elif typeof(b) == TYPE_DICTIONARY:
				if b.has("quantum_teleport_cooldown") and b["quantum_teleport_cooldown"] > 0:
					b["quantum_teleport_cooldown"] -= delta

				if b.has("quantum_scramble_timer") and b["quantum_scramble_timer"] > 0:
					b["quantum_scramble_timer"] -= delta
					if b["quantum_scramble_timer"] <= 0:
						if b.has("base_speed_scrambled"): b["speed"] = b["base_speed_scrambled"]
						if b.has("base_radius_scrambled"): b["radius"] = b["base_radius_scrambled"]
						if b.has("base_damage_mult_scrambled"): b["damage_multiplier"] = b["base_damage_mult_scrambled"]

			var b_x = 0.0
			var b_y = 0.0
			var b_radius = 10.0

			if typeof(b) == TYPE_OBJECT:
				if "x" in b: b_x = float(b.x)
				if "y" in b: b_y = float(b.y)
				if "radius" in b: b_radius = float(b.radius)
			elif typeof(b) == TYPE_DICTIONARY:
				if b.has("x"): b_x = float(b["x"])
				if b.has("y"): b_y = float(b["y"])
				if b.has("radius"): b_radius = float(b["radius"])

			for a in current_anomalies:
				var dx = b_x - float(a.x)
				var dy = b_y - float(a.y)
				var dist = sqrt(dx*dx + dy*dy)

				if dist <= float(a.radius) + b_radius:
					var has_scramble = false
					var scramble_timer = 0.0
					if typeof(b) == TYPE_OBJECT and b.has_method("has_meta"):
						if b.has_meta("quantum_scramble_timer"):
							has_scramble = true
							scramble_timer = float(b.get_meta("quantum_scramble_timer"))
					elif typeof(b) == TYPE_DICTIONARY:
						if b.has("quantum_scramble_timer"):
							has_scramble = true
							scramble_timer = float(b["quantum_scramble_timer"])

					if not has_scramble or scramble_timer <= 0:
						var dur = 2.0 + randf() * 3.0
						if typeof(b) == TYPE_OBJECT and b.has_method("set_meta"):
							b.set_meta("quantum_scramble_timer", dur)
							if not b.has_meta("base_speed_scrambled"):
								b.set_meta("base_speed_scrambled", b.speed if "speed" in b else 5.0)
							if not b.has_meta("base_radius_scrambled"):
								b.set_meta("base_radius_scrambled", b.radius if "radius" in b else 10.0)
							if not b.has_meta("base_damage_mult_scrambled"):
								b.set_meta("base_damage_mult_scrambled", b.damage_multiplier if "damage_multiplier" in b else 1.0)

							if "speed" in b: b.speed = float(b.get_meta("base_speed_scrambled")) * (0.5 + randf() * 1.5)
							if "radius" in b: b.radius = max(5.0, float(b.get_meta("base_radius_scrambled")) * (0.5 + randf() * 1.0))
							if "damage_multiplier" in b: b.damage_multiplier = float(b.get_meta("base_damage_mult_scrambled")) * (0.5 + randf() * 2.0)
						elif typeof(b) == TYPE_DICTIONARY:
							b["quantum_scramble_timer"] = dur
							if not b.has("base_speed_scrambled"): b["base_speed_scrambled"] = b.get("speed", 5.0)
							if not b.has("base_radius_scrambled"): b["base_radius_scrambled"] = b.get("radius", 10.0)
							if not b.has("base_damage_mult_scrambled"): b["base_damage_mult_scrambled"] = b.get("damage_multiplier", 1.0)

							b["speed"] = b["base_speed_scrambled"] * (0.5 + randf() * 1.5)
							b["radius"] = max(5.0, b["base_radius_scrambled"] * (0.5 + randf() * 1.0))
							b["damage_multiplier"] = b["base_damage_mult_scrambled"] * (0.5 + randf() * 2.0)

					var teleport_chance = 0.05
					var near_center = dist < (float(a.radius) * 0.3)

					var can_teleport = true
					if typeof(b) == TYPE_OBJECT and b.has_method("has_meta") and b.has_meta("quantum_teleport_cooldown") and float(b.get_meta("quantum_teleport_cooldown")) > 0:
						can_teleport = false
					elif typeof(b) == TYPE_DICTIONARY and b.has("quantum_teleport_cooldown") and b["quantum_teleport_cooldown"] > 0:
						can_teleport = false

					if can_teleport:
						if near_center or randf() < teleport_chance:
							var linked = null
							for h in current_anomalies:
								if "id" in h and h.id == a.linked_id:
									linked = h
									break

							if linked != null:
								if typeof(b) == TYPE_OBJECT:
									if "x" in b: b.x = linked.x
									if "y" in b: b.y = linked.y
									if b.has_method("set_meta"): b.set_meta("quantum_teleport_cooldown", 1.0)
									if b.has_method("set_meta"): b.set_meta("teleport_effect_timer", 0.5)
								elif typeof(b) == TYPE_DICTIONARY:
									b["x"] = linked["x"]
									b["y"] = linked["y"]
									b["quantum_teleport_cooldown"] = 1.0
									b["teleport_effect_timer"] = 0.5

GAME_MODES['quantum_anomalies'] = QuantumAnomaliesMode.new()
