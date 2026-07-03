class_name ShrinkingHazardsArena
extends ProceduralArena

var hazard_spawn_timer: float = 0.0

func _init(_arena_size: float = 2000.0, _num_rooms: int = 5, _seed = null):
	super(_arena_size, _num_rooms, _seed)

func update_zone(current_tick: int, delta: float) -> void:
	var is_new_tick = current_tick != last_tick
	super.update_zone(current_tick, delta)

	if is_new_tick:
		hazard_spawn_timer += delta
		# Spawn a new expanding hazard on the edge of the safe zone every 5 seconds
		if hazard_spawn_timer >= 5.0:
			hazard_spawn_timer = 0.0

			var angle = randf_range(0.0, PI * 2)
			var spawn_dist = safe_zone_radius
			var cx = safe_zone_center[0]
			var cy = safe_zone_center[1]

			var hx = cx + cos(angle) * spawn_dist
			var hy = cy + sin(angle) * spawn_dist

			# Clamp to arena bounds
			hx = max(0.0, min(width, hx))
			hy = max(0.0, min(height, hy))

			var h_id = 10000 + hazards.size() + (randi() % 1000)

			# Use ProceduralArena.Hazard if available, else a dictionary
			var ProceduralArenaScript = load("res://src/arena/procedural_arena.gd")
			if ProceduralArenaScript and ProceduralArenaScript.has_source_code():
				var new_hazard = ProceduralArenaScript.Hazard.new(h_id, hx, hy, 10.0, "shrinking_zone_hazard", 25.0)
				new_hazard.target_radius = 200.0
				hazards.append(new_hazard)
			else:
				var new_hazard = {
					"id": h_id,
					"x": hx,
					"y": hy,
					"radius": 10.0,
					"kind": "shrinking_zone_hazard",
					"damage": 25.0,
					"active": true,
					"target_radius": 200.0
				}
				hazards.append(new_hazard)

		# Manually expand shrinking_zone_hazards
		for h in hazards:
			var kind = h.kind if "kind" in h else (h.get("kind") if typeof(h) == TYPE_DICTIONARY else "")
			var target_radius = h.target_radius if "target_radius" in h else (h.get("target_radius", 0.0) if typeof(h) == TYPE_DICTIONARY else 0.0)

			if kind == "shrinking_zone_hazard":
				var r = h.radius if "radius" in h else (h.get("radius", 0.0) if typeof(h) == TYPE_DICTIONARY else 0.0)
				if r < target_radius:
					var grow_rate = 200.0 / 30.0
					var new_r = r + grow_rate * delta
					if new_r > target_radius:
						new_r = target_radius

					if typeof(h) == TYPE_DICTIONARY:
						h["radius"] = new_r
					else:
						h.radius = new_r
