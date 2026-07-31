extends "res://src/ai/game_modes.gd".GameMode

var spawn_timer: float = 5.0

func _init():
	name = "Noise Hazard"
	description = "Spawns a hazard that pulses and damages players around it based on how fast they are moving (noise)."
	spawn_timer = 5.0

func tick(world, balls: Array, delta: float = 0.016) -> void:
	spawn_timer -= delta

	if world == null:
		return

	var arena = null
	if typeof(world) == TYPE_DICTIONARY and world.has("arena"):
		arena = world["arena"]
	elif typeof(world) == TYPE_OBJECT and "arena" in world:
		arena = world.arena

	if arena == null:
		return

	var hazards = []
	if typeof(arena) == TYPE_DICTIONARY and arena.has("hazards"):
		hazards = arena["hazards"]
	elif typeof(arena) == TYPE_OBJECT and "hazards" in arena:
		hazards = arena.hazards

	if spawn_timer <= 0:
		spawn_timer = 15.0
		var arena_width = 1000
		var arena_height = 1000
		if typeof(arena) == TYPE_DICTIONARY:
			if arena.has("width"): arena_width = arena["width"]
			if arena.has("height"): arena_height = arena["height"]
		elif typeof(arena) == TYPE_OBJECT:
			if "width" in arena: arena_width = arena.width
			if "height" in arena: arena_height = arena.height

		var cx = randf_range(200, arena_width - 200)
		var cy = randf_range(200, arena_height - 200)

		var h = {
			"id": hazards.size() + 98500 + randi() % 1000,
			"x": cx,
			"y": cy,
			"radius": 30.0,
			"kind": "noise_hazard",
			"damage": 0.0,
			"duration": 15.0,
			"pulse_timer": 2.0,
			"pulse_radius": 250.0,
			"active": true
		}
		hazards.append(h)

	var active_hazards = []
	for h in hazards:
		var h_kind = ""
		if typeof(h) == TYPE_DICTIONARY and h.has("kind"): h_kind = h["kind"]
		elif typeof(h) == TYPE_OBJECT and h.has_method("get_meta") and h.has_meta("kind"): h_kind = h.get_meta("kind")
		elif typeof(h) == TYPE_OBJECT and "kind" in h: h_kind = h.kind

		if h_kind == "noise_hazard":
			var dur = 15.0
			if typeof(h) == TYPE_DICTIONARY and h.has("duration"): dur = h["duration"]
			elif typeof(h) == TYPE_OBJECT and "duration" in h: dur = h.duration

			dur -= delta
			if typeof(h) == TYPE_DICTIONARY: h["duration"] = dur
			elif typeof(h) == TYPE_OBJECT: h.duration = dur

			if dur > 0:
				active_hazards.append(h)

				var p_timer = 2.0
				if typeof(h) == TYPE_DICTIONARY and h.has("pulse_timer"): p_timer = h["pulse_timer"]
				elif typeof(h) == TYPE_OBJECT and "pulse_timer" in h: p_timer = h.pulse_timer

				p_timer -= delta
				if typeof(h) == TYPE_DICTIONARY: h["pulse_timer"] = p_timer
				elif typeof(h) == TYPE_OBJECT: h.pulse_timer = p_timer

				if p_timer <= 0:
					if typeof(h) == TYPE_DICTIONARY: h["pulse_timer"] = 2.0
					elif typeof(h) == TYPE_OBJECT: h.pulse_timer = 2.0

					var h_x = h["x"] if typeof(h) == TYPE_DICTIONARY else (h.x if typeof(h) == TYPE_OBJECT and "x" in h else 0.0)
					var h_y = h["y"] if typeof(h) == TYPE_DICTIONARY else (h.y if typeof(h) == TYPE_OBJECT and "y" in h else 0.0)
					var h_rad = h["pulse_radius"] if typeof(h) == TYPE_DICTIONARY else (h.pulse_radius if typeof(h) == TYPE_OBJECT and "pulse_radius" in h else 250.0)

					var ev = {"type": "visual_effect", "data": {"type": "noise_pulse", "x": h_x, "y": h_y, "radius": h_rad, "color": "orange", "duration": 0.5}}
					if typeof(world) == TYPE_OBJECT and world.has_method("add_event"):
						world.add_event(ev)
					elif typeof(world) == TYPE_DICTIONARY and world.has("events"):
						world["events"].append(ev)

					for b in balls:
						var alive = true
						if typeof(b) == TYPE_DICTIONARY and b.has("alive"): alive = b["alive"]
						elif typeof(b) == TYPE_OBJECT and "alive" in b: alive = b.alive
						if not alive: continue

						var b_x = b["x"] if typeof(b) == TYPE_DICTIONARY else (b.x if typeof(b) == TYPE_OBJECT and "x" in b else 0.0)
						var b_y = b["y"] if typeof(b) == TYPE_DICTIONARY else (b.y if typeof(b) == TYPE_OBJECT and "y" in b else 0.0)

						var dist = sqrt((b_x - h_x)*(b_x - h_x) + (b_y - h_y)*(b_y - h_y))
						if dist < h_rad:
							var b_vx = b["vx"] if typeof(b) == TYPE_DICTIONARY else (b.vx if typeof(b) == TYPE_OBJECT and "vx" in b else 0.0)
							var b_vy = b["vy"] if typeof(b) == TYPE_DICTIONARY else (b.vy if typeof(b) == TYPE_OBJECT and "vy" in b else 0.0)
							var speed = sqrt(b_vx*b_vx + b_vy*b_vy)
							var damage = speed * 0.1

							if damage > 2.0:
								if typeof(world) == TYPE_OBJECT and world.has_method("_deal_damage"):
									world._deal_damage(null, b, damage)
								else:
									var hp = 100.0
									if typeof(b) == TYPE_DICTIONARY and b.has("hp"): hp = b["hp"]
									elif typeof(b) == TYPE_OBJECT and "hp" in b: hp = b.hp

									hp -= damage

									if typeof(b) == TYPE_DICTIONARY: b["hp"] = hp
									elif typeof(b) == TYPE_OBJECT: b.hp = hp

		else:
			active_hazards.append(h)

	if typeof(arena) == TYPE_DICTIONARY: arena["hazards"] = active_hazards
	elif typeof(arena) == TYPE_OBJECT: arena.hazards = active_hazards
