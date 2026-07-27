extends "res://src/ai/game_modes.gd".GameMode

var event_timer: float = 0.0

func _init():
	name = "Acoustic Disruption Field"
	description = "A new hazard that temporarily disables the perception_radius of any ball inside it, rendering them effectively blind and unable to target enemies, but still able to move freely."
	event_timer = 0.0

func tick(world, balls: Array, delta: float = 0.016) -> void:
	event_timer += delta

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

	if event_timer >= 15.0:
		event_timer = 0.0
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
			"id": hazards.size() + 98000 + randi() % 1000,
			"x": cx,
			"y": cy,
			"radius": 100.0,
			"kind": "acoustic_disruption",
			"damage": 0.0,
			"duration": 10.0,
			"active": true
		}
		hazards.append(h)

	var active_hazards = []
	for h in hazards:
		var h_kind = ""
		if typeof(h) == TYPE_DICTIONARY and h.has("kind"): h_kind = h["kind"]
		elif typeof(h) == TYPE_OBJECT and h.has_method("get_meta") and h.has_meta("kind"): h_kind = h.get_meta("kind")
		elif typeof(h) == TYPE_OBJECT and "kind" in h: h_kind = h.kind

		if h_kind == "acoustic_disruption":
			var dur = 10.0
			if typeof(h) == TYPE_DICTIONARY and h.has("duration"): dur = h["duration"]
			elif typeof(h) == TYPE_OBJECT and "duration" in h: dur = h.duration

			dur -= delta
			if typeof(h) == TYPE_DICTIONARY: h["duration"] = dur
			elif typeof(h) == TYPE_OBJECT: h.duration = dur

			if dur > 0:
				active_hazards.append(h)
				var h_x = h["x"] if typeof(h) == TYPE_DICTIONARY else (h.x if typeof(h) == TYPE_OBJECT and "x" in h else 0.0)
				var h_y = h["y"] if typeof(h) == TYPE_DICTIONARY else (h.y if typeof(h) == TYPE_OBJECT and "y" in h else 0.0)
				var h_rad = h["radius"] if typeof(h) == TYPE_DICTIONARY else (h.radius if typeof(h) == TYPE_OBJECT and "radius" in h else 100.0)

				for b in balls:
					var alive = true
					if typeof(b) == TYPE_DICTIONARY and b.has("alive"): alive = b["alive"]
					elif typeof(b) == TYPE_OBJECT and "alive" in b: alive = b.alive
					if not alive: continue

					var b_x = b["x"] if typeof(b) == TYPE_DICTIONARY else (b.x if typeof(b) == TYPE_OBJECT and "x" in b else 0.0)
					var b_y = b["y"] if typeof(b) == TYPE_DICTIONARY else (b.y if typeof(b) == TYPE_OBJECT and "y" in b else 0.0)
					var b_rad = 10.0
					if typeof(b) == TYPE_DICTIONARY and b.has("radius"): b_rad = b["radius"]
					elif typeof(b) == TYPE_OBJECT and "radius" in b: b_rad = b.radius

					var dist_sq = (b_x - h_x)*(b_x - h_x) + (b_y - h_y)*(b_y - h_y)
					if dist_sq < (h_rad + b_rad)*(h_rad + b_rad):
						if typeof(b) == TYPE_DICTIONARY:
							if not b.has("is_acoustically_blinded") or not b["is_acoustically_blinded"]:
								b["is_acoustically_blinded"] = true
								if not b.has("base_perception_radius_acoustic"):
									b["base_perception_radius_acoustic"] = b["perception_radius"] if b.has("perception_radius") else 250.0
								b["perception_radius"] = 0.0
							b["acoustic_blind_timer"] = 0.2
						elif typeof(b) == TYPE_OBJECT:
							var is_blinded = false
							if "is_acoustically_blinded" in b: is_blinded = b.is_acoustically_blinded
							elif b.has_method("get_meta") and b.has_meta("is_acoustically_blinded"): is_blinded = b.get_meta("is_acoustically_blinded")

							if not is_blinded:
								if "is_acoustically_blinded" in b: b.is_acoustically_blinded = true
								elif b.has_method("set_meta"): b.set_meta("is_acoustically_blinded", true)

								var base_p = 250.0
								if "perception_radius" in b: base_p = b.perception_radius

								var has_base = false
								if "base_perception_radius_acoustic" in b: has_base = true
								elif b.has_method("has_meta") and b.has_meta("base_perception_radius_acoustic"): has_base = true

								if not has_base:
									if "base_perception_radius_acoustic" in b: b.base_perception_radius_acoustic = base_p
									elif b.has_method("set_meta"): b.set_meta("base_perception_radius_acoustic", base_p)

								if "perception_radius" in b: b.perception_radius = 0.0

							if "acoustic_blind_timer" in b: b.acoustic_blind_timer = 0.2
							elif b.has_method("set_meta"): b.set_meta("acoustic_blind_timer", 0.2)
		else:
			active_hazards.append(h)

	if typeof(arena) == TYPE_DICTIONARY: arena["hazards"] = active_hazards
	elif typeof(arena) == TYPE_OBJECT: arena.hazards = active_hazards

	for b in balls:
		if typeof(b) == TYPE_DICTIONARY:
			if b.has("is_acoustically_blinded") and b["is_acoustically_blinded"]:
				var t = b.get("acoustic_blind_timer", 0.0) - delta
				b["acoustic_blind_timer"] = t
				if t <= 0:
					b["is_acoustically_blinded"] = false
					if b.has("base_perception_radius_acoustic"):
						b["perception_radius"] = b["base_perception_radius_acoustic"]
						b.erase("base_perception_radius_acoustic")
		elif typeof(b) == TYPE_OBJECT:
			var is_blinded = false
			if "is_acoustically_blinded" in b: is_blinded = b.is_acoustically_blinded
			elif b.has_method("get_meta") and b.has_meta("is_acoustically_blinded"): is_blinded = b.get_meta("is_acoustically_blinded")

			if is_blinded:
				var t = 0.0
				if "acoustic_blind_timer" in b: t = b.acoustic_blind_timer
				elif b.has_method("get_meta") and b.has_meta("acoustic_blind_timer"): t = b.get_meta("acoustic_blind_timer")
				t -= delta
				if "acoustic_blind_timer" in b: b.acoustic_blind_timer = t
				elif b.has_method("set_meta"): b.set_meta("acoustic_blind_timer", t)

				if t <= 0:
					if "is_acoustically_blinded" in b: b.is_acoustically_blinded = false
					elif b.has_method("set_meta"): b.set_meta("is_acoustically_blinded", false)

					var has_base = false
					if "base_perception_radius_acoustic" in b: has_base = true
					elif b.has_method("has_meta") and b.has_meta("base_perception_radius_acoustic"): has_base = true

					if has_base:
						var base_val = 250.0
						if "base_perception_radius_acoustic" in b: base_val = b.base_perception_radius_acoustic
						elif b.has_method("get_meta") and b.has_meta("base_perception_radius_acoustic"): base_val = b.get_meta("base_perception_radius_acoustic")

						if "perception_radius" in b: b.perception_radius = base_val
