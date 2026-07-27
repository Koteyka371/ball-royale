extends "res://src/ai/game_modes.gd"

var laser_damage_per_second: float = 100.0

func _init() -> void:
	name = "Bouncing Laser Core"
	description = "A single indestructible laser core spawns in the center of the map. It fires two continuous solid beam lasers in opposite directions and slowly rotates. Over time, the core bounces around the arena like a paddle ball, randomly changing direction when hitting a wall, making dodging extremely unpredictable."

func setup(world, balls: Array) -> void:
	if world != null and typeof(world) == TYPE_DICTIONARY and "arena" in world and typeof(world.arena) == TYPE_DICTIONARY and "hazards" in world.arena:
		var arena_w = world.arena.get("width", 800.0)
		var arena_h = world.arena.get("height", 600.0)
		var cx = arena_w / 2.0
		var cy = arena_h / 2.0

		# In GDScript, ProceduralArena is accessed differently depending on where we are,
		# but usually we use the script directly.
		var Hazard = load("res://src/arena/procedural_arena.gd").Hazard
		var core = Hazard.new(1576, cx, cy, 30.0, "bouncing_laser_core", 0.0)

		var init_angle = randf_range(0.0, PI * 2.0)
		var speed = 250.0
		var vx = cos(init_angle) * speed
		var vy = sin(init_angle) * speed

		var core_state = {
			"vx": vx,
			"vy": vy,
			"angle": 0.0,
			"rotation_speed": 1.0
		}
		core.set_meta("core_state", core_state)

		world.arena.hazards.append(core)
	elif world != null and typeof(world) == TYPE_OBJECT and "arena" in world and world.arena != null and "hazards" in world.arena:
		var arena_w = world.arena.get("width") if "width" in world.arena else 800.0
		var arena_h = world.arena.get("height") if "height" in world.arena else 600.0
		var cx = arena_w / 2.0
		var cy = arena_h / 2.0

		# It's an object with .arena object
		var HazardScript = load("res://src/arena/procedural_arena.gd")
		var core = null
		if HazardScript and HazardScript.has_method("Hazard"):
			pass # Cannot easily instantiate inner classes in Godot 3 via reflection.
		else:
			# Just try direct
			var pr = load("res://src/arena/procedural_arena.gd").new()
			# This is tricky in Godot 3/4. Usually GameModes use ProceduralArenaScript2 or similar global.
			pass

		# Safer fallback if Hazard fails to load:
		# Just construct a dictionary if world is dict, but here world is object
		# Find another hazard and copy its class
		# This is often what game_modes.gd does.
		# We'll use a hack to get the class from `ProceduralArenaScript.Hazard` if it exists.

		# Look at game_modes.gd for how they instantiate Hazards:
		# e.g., ProceduralArenaScript.Hazard.new(...)

		var ProceduralArenaScript = load("res://src/arena/procedural_arena.gd")
		var core_obj = ProceduralArenaScript.Hazard.new(1576, cx, cy, 30.0, "bouncing_laser_core", 0.0)

		var init_angle_obj = randf_range(0.0, PI * 2.0)
		var speed_obj = 250.0
		var vx_obj = cos(init_angle_obj) * speed_obj
		var vy_obj = sin(init_angle_obj) * speed_obj

		var core_state_obj = {
			"vx": vx_obj,
			"vy": vy_obj,
			"angle": 0.0,
			"rotation_speed": 1.0
		}
		core_obj.set_meta("core_state", core_state_obj)

		world.arena.hazards.append(core_obj)

func tick(world, balls: Array, delta: float = 0.016) -> void:
	if world == null:
		return

	var hazards = []
	var arena_w = 800.0
	var arena_h = 600.0

	if typeof(world) == TYPE_DICTIONARY and "arena" in world and typeof(world.arena) == TYPE_DICTIONARY and "hazards" in world.arena:
		hazards = world.arena.hazards
		arena_w = world.arena.get("width", 800.0)
		arena_h = world.arena.get("height", 600.0)
	elif typeof(world) == TYPE_OBJECT and "arena" in world and world.arena != null and "hazards" in world.arena:
		hazards = world.arena.hazards
		arena_w = world.arena.get("width") if "width" in world.arena else 800.0
		arena_h = world.arena.get("height") if "height" in world.arena else 600.0
	else:
		return

	var core = null
	for h in hazards:
		var h_kind = ""
		if typeof(h) == TYPE_DICTIONARY and "kind" in h: h_kind = h.kind
		elif typeof(h) == TYPE_OBJECT and h.has_method("get_meta") and h.has_meta("kind"): h_kind = h.get_meta("kind")
		elif typeof(h) == TYPE_OBJECT and "kind" in h: h_kind = h.kind

		if h_kind == "bouncing_laser_core":
			core = h
			break

	if core == null:
		return

	var core_state = {}
	if typeof(core) == TYPE_DICTIONARY and "meta_core_state" in core:
		core_state = core.meta_core_state
	elif typeof(core) == TYPE_OBJECT and core.has_method("has_meta") and core.has_meta("core_state"):
		core_state = core.get_meta("core_state")
	else:
		return

	var vx = core_state.get("vx", 0.0)
	var vy = core_state.get("vy", 0.0)
	var angle = core_state.get("angle", 0.0)
	var rot_speed = core_state.get("rotation_speed", 1.0)

	var cx = 0.0
	var cy = 0.0
	var cr = 30.0

	if typeof(core) == TYPE_DICTIONARY:
		cx = core.get("x", 0.0)
		cy = core.get("y", 0.0)
		cr = core.get("radius", 30.0)
	else:
		cx = core.x
		cy = core.y
		cr = core.radius

	cx += vx * delta
	cy += vy * delta
	angle += rot_speed * delta

	var bounced = false
	if cx - cr < 50.0:
		cx = 50.0 + cr
		vx = abs(vx)
		bounced = true
	elif cx + cr > arena_w - 50.0:
		cx = arena_w - 50.0 - cr
		vx = -abs(vx)
		bounced = true

	if cy - cr < 50.0:
		cy = 50.0 + cr
		vy = abs(vy)
		bounced = true
	elif cy + cr > arena_h - 50.0:
		cy = arena_h - 50.0 - cr
		vy = -abs(vy)
		bounced = true

	if bounced:
		var speed = sqrt(vx * vx + vy * vy)
		var current_angle = atan2(vy, vx)
		var deflection = randf_range(-PI/6.0, PI/6.0)
		var new_angle = current_angle + deflection
		vx = cos(new_angle) * speed
		vy = sin(new_angle) * speed

		# Pick 1 or -1
		var dir = 1.0 if randf() > 0.5 else -1.0
		rot_speed = randf_range(0.5, 2.0) * dir

	core_state["vx"] = vx
	core_state["vy"] = vy
	core_state["angle"] = angle
	core_state["rotation_speed"] = rot_speed

	if typeof(core) == TYPE_DICTIONARY:
		core["x"] = cx
		core["y"] = cy
		core["meta_core_state"] = core_state
	else:
		core.x = cx
		core.y = cy
		core.set_meta("core_state", core_state)

	# Deal damage
	for b in balls:
		var b_alive = b.get("alive", true) if typeof(b) == TYPE_DICTIONARY else b.get("alive")
		if b_alive == null: b_alive = true
		var b_type = b.get("ball_type", "") if typeof(b) == TYPE_DICTIONARY else b.get("ball_type")

		if not b_alive or b_type == "spectator":
			continue

		var bx = b.get("x", 0.0) if typeof(b) == TYPE_DICTIONARY else b.get("x")
		var by = b.get("y", 0.0) if typeof(b) == TYPE_DICTIONARY else b.get("y")
		var br = b.get("radius", 15.0) if typeof(b) == TYPE_DICTIONARY else b.get("radius")

		var dx = cos(angle)
		var dy = sin(angle)

		var dist_to_line = abs((bx - cx) * dy - (by - cy) * dx)
		var laser_width = 15.0

		if dist_to_line <= br + laser_width:
			var dmg = laser_damage_per_second * delta
			if typeof(b) == TYPE_DICTIONARY:
				var hp = b.get("hp", 100.0)
				hp -= dmg
				if hp <= 0.0:
					hp = 0.0
					b["alive"] = false
				b["hp"] = hp
			else:
				if b.has_method("take_damage"):
					b.take_damage(dmg)
				else:
					var hp = b.get("hp")
					if hp != null:
						hp -= dmg
						if hp <= 0.0:
							hp = 0.0
							b.set("alive", false)
						b.set("hp", hp)
