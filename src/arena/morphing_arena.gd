class_name MorphingArena
extends BasicArena

var morph_timer: float = 0.0
var morph_duration: float = 60.0
var current_shape_idx: int = 0
var target_shape_idx: int = 0
var transition_progress: float = 0.0

func _init(_arena_size: float = 2000.0, _seed = null):
	super(_arena_size, _seed)

func get_sdf(x: float, y: float, r: float, shape_idx: int) -> float:
	var cx = width / 2.0
	var cy = height / 2.0
	var dx = x - cx
	var dy = y - cy

	if shape_idx == 0:
		var adx = abs(dx) - r
		var ady = abs(dy) - r
		var max_x = max(adx, 0.0)
		var max_y = max(ady, 0.0)
		return sqrt(max_x * max_x + max_y * max_y) + min(max(adx, ady), 0.0)
	elif shape_idx == 1:
		return sqrt(dx * dx + dy * dy) - r
	elif shape_idx == 2:
		var w = r
		var h = r / 3.0

		var adx1 = abs(dx) - w
		var ady1 = abs(dy) - h
		var max_x1 = max(adx1, 0.0)
		var max_y1 = max(ady1, 0.0)
		var d1 = sqrt(max_x1 * max_x1 + max_y1 * max_y1) + min(max(adx1, ady1), 0.0)

		var adx2 = abs(dx) - h
		var ady2 = abs(dy) - w
		var max_x2 = max(adx2, 0.0)
		var max_y2 = max(ady2, 0.0)
		var d2 = sqrt(max_x2 * max_x2 + max_y2 * max_y2) + min(max(adx2, ady2), 0.0)

		return min(d1, d2)
	return 0.0

func evaluate_sdf(x: float, y: float, base_radius: float) -> float:
	var d1 = get_sdf(x, y, base_radius, current_shape_idx)
	var d2 = get_sdf(x, y, base_radius, target_shape_idx)
	return d1 * (1.0 - transition_progress) + d2 * transition_progress

func update_zone(current_tick: int, delta: float) -> void:
	super.update_zone(current_tick, delta)
	morph_timer += delta

	var cycle_time = fmod(morph_timer, morph_duration)
	var cycle_idx = int(morph_timer / morph_duration)
	current_shape_idx = cycle_idx % 3
	target_shape_idx = (cycle_idx + 1) % 3

	if cycle_time < 10.0:
		transition_progress = cycle_time / 10.0
	else:
		transition_progress = 1.0

func is_point_inside(x: float, y: float, radius: float) -> bool:
	if not super.is_point_inside(x, y, radius):
		return false

	var base_r = width / 2.0 - 100.0
	var dist = evaluate_sdf(x, y, base_r)
	return dist <= -radius + 1.0

func clamp_position(x: float, y: float, radius: float) -> Array:
	var res = super.clamp_position(x, y, radius)
	var new_x = res[0]
	var new_y = res[1]
	var bounced = res[2]

	var base_r = width / 2.0 - 100.0
	var dist = evaluate_sdf(new_x, new_y, base_r)

	if dist > -radius + 1.0:
		var eps = 0.1
		var gx = evaluate_sdf(new_x + eps, new_y, base_r) - evaluate_sdf(new_x - eps, new_y, base_r)
		var gy = evaluate_sdf(new_x, new_y + eps, base_r) - evaluate_sdf(new_x, new_y - eps, base_r)
		var length = sqrt(gx * gx + gy * gy)

		if length > 0.0001:
			gx /= length
			gy /= length
			var push_dist = dist + radius
			new_x -= gx * push_dist
			new_y -= gy * push_dist
		else:
			var cx = width / 2.0
			var cy = height / 2.0
			var dir_x = cx - new_x
			var dir_y = cy - new_y
			var l = sqrt(dir_x * dir_x + dir_y * dir_y)
			if l > 0.0001:
				new_x += (dir_x / l) * 5.0
				new_y += (dir_y / l) * 5.0

		bounced = true

	return [new_x, new_y, bounced]
