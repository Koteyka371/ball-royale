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

	# Generate quantum teleporters
	var num_quantum = max(1, int(width / 1000.0))
	for p in range(num_quantum):
		var q1_id = hazards.size() + 11000 + p*2
		var q2_id = hazards.size() + 11000 + p*2 + 1

		var q1_pt = get_random_spawn_point(30.0)

		# Find distant point
		var q2_pt = get_random_spawn_point(30.0)
		var best_dist = (q1_pt[0] - q2_pt[0])*(q1_pt[0] - q2_pt[0]) + (q1_pt[1] - q2_pt[1])*(q1_pt[1] - q2_pt[1])
		for i in range(10):
			var t_pt = get_random_spawn_point(30.0)
			var dist = (q1_pt[0] - t_pt[0])*(q1_pt[0] - t_pt[0]) + (q1_pt[1] - t_pt[1])*(q1_pt[1] - t_pt[1])
			if dist > best_dist:
				best_dist = dist
				q2_pt = t_pt

		var q1 = preload("res://src/arena/procedural_arena.gd").Hazard.new(q1_id, q1_pt[0], q1_pt[1], 30.0, "quantum_teleporter", 0.0)
		q1.set_meta("target_x", q2_pt[0])
		q1.set_meta("target_y", q2_pt[1])

		var q2 = preload("res://src/arena/procedural_arena.gd").Hazard.new(q2_id, q2_pt[0], q2_pt[1], 30.0, "quantum_teleporter", 0.0)
		q2.set_meta("target_x", q1_pt[0])
		q2.set_meta("target_y", q1_pt[1])

		hazards.append(q1)
		hazards.append(q2)

func get_random_spawn_point(radius: float) -> Array:
	return [rng.randf_range(radius, width - radius), rng.randf_range(radius, height - radius)]

func is_point_inside(x: float, y: float, radius: float) -> bool:
	if not (radius <= x and x <= width - radius and radius <= y and y <= height - radius):
		return false
	var cx = safe_zone_center[0]
	var cy = safe_zone_center[1]
	var dist = sqrt((x - cx)*(x - cx) + (y - cy)*(y - cy))
	return dist <= max(0.0, safe_zone_radius - radius)

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
	if dist > max(0.0, safe_zone_radius - radius):
		if dist > 0.0001:
			var dir_x = (new_x - cx) / dist
			var dir_y = (new_y - cy) / dist
			new_x = cx + dir_x * max(0.0, safe_zone_radius - radius)
			new_y = cy + dir_y * max(0.0, safe_zone_radius - radius)
		else:
			new_x = cx
			new_y = cy
		bounced = true

	return [new_x, new_y, bounced]

func update_zone(current_tick: int, delta: float) -> void:
	if current_tick != last_tick:
		last_tick = current_tick
		if safe_zone_radius > 0.0:
			safe_zone_radius -= 10.0 * delta
			if safe_zone_radius <= 0.0:
				safe_zone_radius = 0.0

			# Black hole spawning and merging when safe zone is very small
			if safe_zone_radius <= 100.0:
				# Spawn new black holes occasionally
				if current_tick % 60 == 0 and randf() < 0.5:
					var angle = randf_range(0, PI * 2)
					var dist = randf_range(0, max(1.0, safe_zone_radius))
					var cx = width / 2.0
					var cy = height / 2.0
					var hx = cx + cos(angle) * dist
					var hy = cy + sin(angle) * dist
					var bh_id = 20000 + (randi() % 1000)
					if "hazards" in self:
						bh_id += self.hazards.size()

					# Create a basic dictionary since we don't have Hazard imported here
					var bh = preload("res://src/arena/procedural_arena.gd").Hazard.new(bh_id, hx, hy, 20.0, "black_hole", 15.0)
					bh.duration = 1000.0
					if "hazards" in self:
						self.hazards.append(bh)

				if "hazards" in self:
					# Pull all black holes towards the center and merge them
					var bhs = []
					for h in self.hazards:
						if "kind" in h and h.kind == "black_hole":
							bhs.append(h)

					var cx = width / 2.0
					var cy = height / 2.0
					for h in bhs:
						var dx = cx - h.x
						var dy = cy - h.y
						var dist = sqrt(dx*dx + dy*dy)
						if dist > 0.0001:
							h.x += (dx/dist) * 10.0 * delta
							h.y += (dy/dist) * 10.0 * delta

						# Merge logic
						for other in bhs:
							if h.id != other.id and other.duration > 0.0 and h.duration > 0.0:
								var ddx = other.x - h.x
								var ddy = other.y - h.y
								var ddist2 = ddx*ddx + ddy*ddy
								var hr = h.radius
								var orad = other.radius
								if ddist2 < pow(hr + orad, 2) * 0.25:
									# Merge other into h
									h.radius = min(150.0, hr + orad * 0.5)
									h.damage = h.damage + other.damage * 0.2
									other.duration = 0.0 # Mark for destruction
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
			var kept_hazards = []
			for h in hazards:
				if "kind" in h and h.kind == "quantum_teleporter":
					kept_hazards.append(h)
			hazards.clear()
			for h in kept_hazards:
				hazards.append(h)
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
