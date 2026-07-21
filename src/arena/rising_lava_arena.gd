class_name RisingLavaArena
extends ProceduralArena

var lava_level: float
var lava_rise_speed: float = 10.0

func _init(_arena_size: float = 2000.0, _num_rooms: int = 5, _seed = null):
	super(_arena_size, _num_rooms, _seed)
	boundary_states = {"top": "bouncy", "bottom": "bouncy", "left": "bouncy", "right": "bouncy"}
	boundary_health = {"top": 2000.0, "bottom": 2000.0, "left": 2000.0, "right": 2000.0}
	lava_level = _arena_size

func generate() -> void:
	super.generate()
	rooms.clear()
	corridors.clear()
	hazards.clear()

	var w = width
	var h = height

	rooms.append({
		"x": w / 2.0 - 200.0,
		"y": h - 300.0,
		"width": 400.0,
		"height": 200.0
	})

	for i in range(15):
		var rw = randf_range(150.0, 300.0)
		var rh = randf_range(100.0, 200.0)
		var rx = randf_range(50.0, w - rw - 50.0)
		var ry = randf_range(50.0, h - 400.0)

		var overlap = false
		for r in rooms:
			if not (rx + rw + 20.0 < r.x or rx > r.x + r.width + 20.0 or ry + rh + 20.0 < r.y or ry > r.y + r.height + 20.0):
				overlap = true
				break

		if not overlap:
			rooms.append({
				"x": rx,
				"y": ry,
				"width": rw,
				"height": rh
			})

func update_zone(current_tick: int, delta: float) -> void:
	var is_new_tick = current_tick != last_tick
	super.update_zone(current_tick, delta)

	if is_new_tick:
		lava_level -= lava_rise_speed * delta
		if lava_level < 0.0:
			lava_level = 0.0

		var surviving_rooms = []
		for r in rooms:
			if r.y < lava_level:
				surviving_rooms.append(r)
		rooms = surviving_rooms

		var surviving_hazards = []
		for h in hazards:
			if typeof(h) == TYPE_DICTIONARY:
				if h.get("kind", "") != "rising_lava_zone":
					surviving_hazards.append(h)
			elif h.get("kind") != "rising_lava_zone":
				surviving_hazards.append(h)
		hazards = surviving_hazards

		if lava_level < height:
			var num_hazards = int(ceil(width / 200.0))
			for i in range(num_hazards):
				var hx = i * 200.0 + 100.0
				var hy = lava_level + 100.0
				var h_id = 20000 + hazards.size() + i

				var ProceduralArenaScript = load("res://src/arena/procedural_arena.gd")
				if ProceduralArenaScript and ProceduralArenaScript.has_source_code():
					var new_hazard = ProceduralArenaScript.Hazard.new(h_id, hx, hy, 120.0, "rising_lava_zone", 50.0)
					hazards.append(new_hazard)
				else:
					var new_hazard = {
						"id": h_id,
						"x": hx,
						"y": hy,
						"radius": 120.0,
						"kind": "rising_lava_zone",
						"damage": 50.0,
						"active": true
					}
					hazards.append(new_hazard)

func is_point_inside(px: float, py: float, radius: float) -> bool:
	return super.is_point_inside(px, py, radius)
