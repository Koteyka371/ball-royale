class_name MorphingArena
extends ProceduralArena

var boundary_states: Dictionary = {"top": "bouncy", "bottom": "bouncy", "left": "bouncy", "right": "bouncy"}
var boundary_health: Dictionary = {"top": 2000.0, "bottom": 2000.0, "left": 2000.0, "right": 2000.0}

var current_tick: int = 0

func _init(_arena_size: float = 2000.0, _num_rooms: int = 0, _seed = null):
	super(_arena_size, _num_rooms, _seed)
	name = "morphing"

func generate() -> void:
	super.generate()
	rooms.clear()
	corridors.clear()

func sdf_box(px: float, py: float, w: float, h: float) -> float:
	var dx = abs(px) - w / 2.0
	var dy = abs(py) - h / 2.0
	return sqrt(max(dx, 0.0) * max(dx, 0.0) + max(dy, 0.0) * max(dy, 0.0)) + min(max(dx, dy), 0.0)

func sdf_cross(px: float, py: float, span: float, thickness: float) -> float:
	var d1 = sdf_box(px, py, thickness, span)
	var d2 = sdf_box(px, py, span, thickness)
	return min(d1, d2)

func sdf_circle(px: float, py: float, r: float) -> float:
	return sqrt(px * px + py * py) - r

func get_sdf(x: float, y: float) -> float:
	var phase = float(current_tick % 3600) / 3600.0
	var cx = width / 2.0
	var cy = height / 2.0
	var px = x - cx
	var py = y - cy

	var size = min(width, height) - 100.0

	var shape0 = sdf_box(px, py, size, size)
	var shape1 = sdf_circle(px, py, size / 2.0)
	var shape2 = sdf_cross(px, py, size, size * 0.4)
	var shapes = [shape0, shape1, shape2]

	var idx1 = int(phase * 3.0) % 3
	var idx2 = (idx1 + 1) % 3
	var t = (phase * 3.0) - float(idx1)

	t = t * t * (3.0 - 2.0 * t)

	return (1.0 - t) * shapes[idx1] + t * shapes[idx2]

func is_point_inside(x: float, y: float, radius: float) -> bool:
	return get_sdf(x, y) <= -radius + 1.0

func clamp_position(x: float, y: float, radius: float) -> Array:
	var val = get_sdf(x, y)
	if val <= -radius + 1.0:
		return [x, y, false]

	var new_x = x
	var new_y = y
	var eps = 1.0

	for i in range(30):
		val = get_sdf(new_x, new_y)
		if val <= -radius + 1.0:
			break

		var dx = get_sdf(new_x + eps, new_y) - get_sdf(new_x - eps, new_y)
		var dy = get_sdf(new_x, new_y + eps) - get_sdf(new_x, new_y - eps)
		var gl = sqrt(dx * dx + dy * dy)

		var nx = 0.0
		var ny = 0.0

		if gl > 0.0001:
			nx = dx / gl
			ny = dy / gl
		else:
			var cx = width / 2.0
			var cy = height / 2.0
			var vec_x = cx - new_x
			var vec_y = cy - new_y
			var vec_len = sqrt(vec_x * vec_x + vec_y * vec_y)
			if vec_len > 0.0001:
				nx = -vec_x / vec_len
				ny = -vec_y / vec_len
			else:
				nx = 1.0
				ny = 0.0

		var move = (val + radius) * 0.9
		new_x -= nx * move
		new_y -= ny * move

	return [new_x, new_y, true]

func update_zone(ctick: int, delta: float) -> void:
	current_tick = ctick
	super.update_zone(ctick, delta)

	for hazard in hazards:
		var res = clamp_position(hazard.x, hazard.y, hazard.radius)
		if res[2]:
			hazard.x = res[0]
			hazard.y = res[1]

	if "platforms" in self:
		for platform in self.platforms:
			var rad = min(platform.width, platform.height) / 2.0
			var res = clamp_position(platform.x, platform.y, rad)
			if res[2]:
				platform.x = res[0]
				platform.y = res[1]
