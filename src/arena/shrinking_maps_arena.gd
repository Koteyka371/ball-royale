class_name ShrinkingMapsArena
extends ProceduralArena
var boundary_states: Dictionary = {"top": "bouncy", "bottom": "bouncy", "left": "bouncy", "right": "bouncy"}
var boundary_health: Dictionary = {"top": 2000.0, "bottom": 2000.0, "left": 2000.0, "right": 2000.0}

var min_x: float
var min_y: float
var max_x: float
var max_y: float

func _init(_arena_size: float = 2000.0, _num_rooms: int = 5, _seed = null):
	super(_arena_size, _num_rooms, _seed)
	min_x = 0.0
	min_y = 0.0
	max_x = width
	max_y = height

func update_zone(current_tick: int, delta: float) -> void:
	var is_new_tick = current_tick != last_tick
	super.update_zone(current_tick, delta)

	if is_new_tick:
		var shrink_rate = 10.0 * delta

		if max_x - min_x > 50.0:
			min_x += shrink_rate
			max_x -= shrink_rate

		if max_y - min_y > 50.0:
			min_y += shrink_rate
			max_y -= shrink_rate

		for hazard in hazards:
			hazard.x = max(min_x + hazard.radius, min(max_x - hazard.radius, hazard.x))
			hazard.y = max(min_y + hazard.radius, min(max_y - hazard.radius, hazard.y))

		# Assuming platforms exist in gdscript and are implemented similar to hazards
		if "platforms" in self:
			for p in self.platforms:
				var pw_half = p.width / 2.0
				var ph_half = p.height / 2.0
				p.x = max(min_x + pw_half, min(max_x - pw_half, p.x))
				p.y = max(min_y + ph_half, min(max_y - ph_half, p.y))

func is_point_inside(x: float, y: float, radius: float) -> bool:
	if not (min_x + radius <= x and x <= max_x - radius and min_y + radius <= y and y <= max_y - radius):
		return false
	return super.is_point_inside(x, y, radius)

func clamp_position(x: float, y: float, radius: float) -> Array:
	var bounced = false
	var new_x = x
	var new_y = y

	if new_x < min_x + radius:
		new_x = min_x + radius
		bounced = true
	elif new_x > max_x - radius:
		new_x = max_x - radius
		bounced = true

	if new_y < min_y + radius:
		new_y = min_y + radius
		bounced = true
	elif new_y > max_y - radius:
		new_y = max_y - radius
		bounced = true

	var res = super.clamp_position(new_x, new_y, radius)
	var res_x = res[0]
	var res_y = res[1]
	var proc_bounced = res[2]

	var final_x = max(min_x + radius, min(max_x - radius, res_x))
	var final_y = max(min_y + radius, min(max_y - radius, res_y))

	if final_x != res_x or final_y != res_y:
		proc_bounced = true

	return [final_x, final_y, bounced or proc_bounced]
