class_name BasicArena
extends RefCounted

var width: float
var height: float
var rng: RandomNumberGenerator

var safe_zone_radius: float
var safe_zone_center: Array
var target_safe_zone_center: Array
var zone_migration_timer: float = 0.0
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
	target_safe_zone_center = [] + safe_zone_center
	zone_migration_timer = 0.0
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
		safe_zone_radius -= 10.0 * delta
		if safe_zone_radius < 50.0:
			safe_zone_radius = 50.0
		zone_migration_timer -= delta
		if zone_migration_timer <= 0.0:
			zone_migration_timer = 10.0
			var tx = randf_range(width * 0.2, width * 0.8)
			var ty = randf_range(height * 0.2, height * 0.8)
			target_safe_zone_center = [tx, ty]

		if target_safe_zone_center.size() > 0:
			var cx = safe_zone_center[0]
			var cy = safe_zone_center[1]
			var tx = target_safe_zone_center[0]
			var ty = target_safe_zone_center[1]
			var dx = tx - cx
			var dy = ty - cy
			var dist = sqrt(dx*dx + dy*dy)
			if dist > 0:
				var speed = 25.0 * delta
				if speed > dist:
					cx = tx
					cy = ty
				else:
					cx += (dx / dist) * speed
					cy += (dy / dist) * speed
				safe_zone_center = [cx, cy]


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
