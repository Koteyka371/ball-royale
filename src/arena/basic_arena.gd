class_name BasicArena
extends RefCounted

var width: float
var height: float
var rng: RandomNumberGenerator

var safe_zone_radius: float
var safe_zone_center: Array
var last_tick: int = -1
var danger_grid: Dictionary = {}
var hazards: Array = []

func _init(_arena_size: float = 2000.0, _seed = null):
	width = _arena_size
	height = _arena_size
	rng = RandomNumberGenerator.new()
	if _seed != null:
		rng.seed = _seed
	else:
		rng.randomize()

	safe_zone_radius = width * 0.7
	safe_zone_center = [width / 2.0, height / 2.0]
	last_tick = -1

func get_random_spawn_point(radius: float) -> Array:
	return [rng.randf_range(radius, width - radius), rng.randf_range(radius, height - radius)]

func is_point_inside(x: float, y: float, radius: float) -> bool:
	if not (radius <= x and x <= width - radius and radius <= y and y <= height - radius):
		return false
	var cx = safe_zone_center[0]
	var cy = safe_zone_center[1]
	var dist = sqrt((x - cx)*(x - cx) + (y - cy)*(y - cy))
	return dist <= safe_zone_radius - radius

func clamp_position(x: float, y: float, radius: float) -> Array:
	var bounced = false
	var new_x = x
	var new_y = y

	if x < radius:
		new_x = radius
		bounced = true
	elif x > width - radius:
		new_x = width - radius
		bounced = true

	if y < radius:
		new_y = radius
		bounced = true
	elif y > height - radius:
		new_y = height - radius
		bounced = true

	var cx = safe_zone_center[0]
	var cy = safe_zone_center[1]
	var dist = sqrt((new_x - cx)*(new_x - cx) + (new_y - cy)*(new_y - cy))
	if dist > safe_zone_radius - radius:
		if dist > 0.0001:
			var dir_x = (new_x - cx) / dist
			var dir_y = (new_y - cy) / dist
			new_x = cx + dir_x * (safe_zone_radius - radius)
			new_y = cy + dir_y * (safe_zone_radius - radius)
		else:
			new_x = cx
			new_y = cy
		bounced = true

	return [new_x, new_y, bounced]

func update_zone(current_tick: int, delta: float) -> void:
	if current_tick != last_tick:
		last_tick = current_tick
		if safe_zone_radius > 50.0:
			safe_zone_radius -= 10.0 * delta
			if safe_zone_radius <= 50.0:
				safe_zone_radius = 50.0
		else:
			if current_tick % 120 == 0:
				if has_method("_trigger_event"):
					var event_types = ["meteor_shower", "gravity_shift", "orbital_strike", "anomaly_zone", "massive_black_hole_event"]
					call("_trigger_event", event_types[randi() % event_types.size()], current_tick)
				else:
					var event_types = ["meteor_shower", "gravity_shift", "anomaly_zone", "massive_black_hole_event"]
					var event_type = event_types[randi() % event_types.size()]
					if event_type == "meteor_shower":
						for i in range(10):
							var h_x = randf_range(50.0, width - 50.0)
							var h_y = randf_range(50.0, height - 50.0)
							var m_haz = preload("res://src/arena/procedural_arena.gd").Hazard.new(hazards.size() + (randi() % 9000) + 1000, h_x, h_y, 30.0, "meteor", 200.0)
							m_haz.target_radius = 30.0
							m_haz.set_meta("duration", 5.0)
							hazards.append(m_haz)
					elif event_type == "anomaly_zone":
						var zone = preload("res://src/arena/procedural_arena.gd").Hazard.new(hazards.size() + (randi() % 9000) + 1000, width/2, height/2, width/2, "anomaly_zone", 0.0)
						zone.set_meta("duration", 10.0)
						hazards.append(zone)
					elif event_type == "massive_black_hole_event":
						var h_id = 9000 + hazards.size()
						var mbh = preload("res://src/arena/procedural_arena.gd").Hazard.new(h_id, width/2, height/2, 100.0, "massive_black_hole", 10.0)
						mbh.target_radius = 500.0
						mbh.set_meta("duration", 20.0)
						mbh.set_meta("pull_strength", 100.0)
						hazards.append(mbh)
					elif event_type == "gravity_shift":
						var gw = preload("res://src/arena/procedural_arena.gd").Hazard.new(hazards.size() + (randi() % 9000) + 1000, width/2, height/2, width/2, "gravity_well", 10.0)
						gw.set_meta("duration", 10.0)
						hazards.append(gw)

		for h in hazards:
			if "target_radius" in h and h.radius < h.target_radius:
				h.radius += (h.target_radius / 600.0) * delta * 60.0
				if h.radius > h.target_radius:
					h.radius = h.target_radius

		if current_tick % 600 == 0:
			hazards.clear()
			var num_zones = (randi() % 3) + 1
			for i in range(num_zones):
				var x = randf_range(200, width - 200)
				var y = randf_range(200, height - 200)
				var t_radius = randf_range(100.0, 250.0)
				var h = ProceduralArena.Hazard.new(hazards.size(), x, y, 10.0, "trap", 100.0)
				h.target_radius = t_radius
				hazards.append(h)

		if current_tick % 10 == 0:
			_update_danger_grid()

func _update_danger_grid() -> void:
	danger_grid.clear()

	for h in hazards:
		var grid_x = int(h.x / 100)
		var grid_y = int(h.y / 100)
		var r_cells = int(h.radius / 100) + 1
		for i in range(grid_x - r_cells, grid_x + r_cells + 1):
			for j in range(grid_y - r_cells, grid_y + r_cells + 1):
				var cx = i * 100 + 50
				var cy = j * 100 + 50
				var dist = sqrt((cx - h.x)*(cx - h.x) + (cy - h.y)*(cy - h.y))
				if dist <= h.radius + 50:
					var key = str(i) + "," + str(j)
					var current = 0.0
					if danger_grid.has(key):
						current = danger_grid[key]
					danger_grid[key] = current + (h.damage / 10.0)

	var grid_w = int(width / 100) + 1
	var grid_h = int(height / 100) + 1
	for i in range(grid_w):
		for j in range(grid_h):
			var cx = i * 100 + 50
			var cy = j * 100 + 50
			var dist_to_center = sqrt((cx - safe_zone_center[0])*(cx - safe_zone_center[0]) + (cy - safe_zone_center[1])*(cy - safe_zone_center[1]))
			if dist_to_center > safe_zone_radius:
				var key = str(i) + "," + str(j)
				var current = 0.0
				if danger_grid.has(key):
					current = danger_grid[key]
				danger_grid[key] = current + 5.0
