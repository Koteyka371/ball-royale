extends "res://src/ai/game_modes.gd".GameMode

var timer: float = 15.0
var target_x: float = 0.0
var target_y: float = 0.0

func _init() -> void:
	super._init()
	name = "Curling"
	description = "Balls must land as close to a target as possible with ultra-low friction."
	timer = 15.0

func setup(world, balls: Array) -> void:
	if world != null:
		var w_width = 1000.0
		var w_height = 1000.0

		if typeof(world) == TYPE_DICTIONARY and "arena" in world and typeof(world.arena) == TYPE_DICTIONARY:
			world.arena.base_friction = 0.05
			if "width" in world.arena: w_width = world.arena.width
			if "height" in world.arena: w_height = world.arena.height

			target_x = w_width / 2.0
			target_y = w_height / 2.0

			if not ("hazards" in world.arena):
				world.arena.hazards = []
			world.arena.hazards.append({
				"x": target_x,
				"y": target_y,
				"radius": 20.0,
				"kind": "target_marker",
				"active": true
			})
		elif typeof(world) == TYPE_OBJECT and "arena" in world and world.arena != null:
			if typeof(world.arena) == TYPE_OBJECT:
				if world.arena.has_method("set"):
					world.arena.set("base_friction", 0.05)
				elif "base_friction" in world.arena:
					world.arena.base_friction = 0.05

				if "width" in world.arena: w_width = world.arena.width
				elif world.arena.has_method("get_meta") and world.arena.has_meta("width"): w_width = world.arena.get_meta("width")

				if "height" in world.arena: w_height = world.arena.height
				elif world.arena.has_method("get_meta") and world.arena.has_meta("height"): w_height = world.arena.get_meta("height")

				target_x = w_width / 2.0
				target_y = w_height / 2.0

				var target_marker = {
					"x": target_x,
					"y": target_y,
					"radius": 20.0,
					"kind": "target_marker",
					"active": true
				}

				if typeof(world.arena.hazards) == TYPE_ARRAY:
					world.arena.hazards.append(target_marker)
			else:
				target_x = 500.0
				target_y = 500.0
		else:
			target_x = 500.0
			target_y = 500.0
	else:
		target_x = 500.0
		target_y = 500.0

	for b in balls:
		if typeof(b) == TYPE_DICTIONARY:
			b["friction_multiplier"] = 0.05
			b["vx"] = 0.0
			b["vy"] = 0.0
		elif typeof(b) == TYPE_OBJECT:
			if b.has_method("set"):
				b.set("friction_multiplier", 0.05)
				b.set("vx", 0.0)
				b.set("vy", 0.0)
			elif "friction_multiplier" in b:
				b.friction_multiplier = 0.05
				b.vx = 0.0
				b.vy = 0.0

func tick(world, balls: Array, delta: float) -> void:
	timer -= delta
	for b in balls:
		var is_alive = false
		if typeof(b) == TYPE_DICTIONARY and "alive" in b:
			is_alive = b.alive
		elif typeof(b) == TYPE_OBJECT and b.has_method("get"):
			is_alive = b.get("alive")
		elif typeof(b) == TYPE_OBJECT and "alive" in b:
			is_alive = b.alive

		if is_alive:
			if typeof(b) == TYPE_DICTIONARY:
				b["friction_multiplier"] = 0.05
				b["is_frictionless"] = true
			elif typeof(b) == TYPE_OBJECT:
				if b.has_method("set"):
					b.set("friction_multiplier", 0.05)
					b.set("is_frictionless", true)
				elif "friction_multiplier" in b:
					b.friction_multiplier = 0.05
					b.is_frictionless = true

func check_winner(world, balls: Array):
	if timer > 0:
		return null

	var closest_dist = 99999999.0
	var winner_team = null

	for b in balls:
		var is_alive = false
		var b_type = ""
		var b_x = 0.0
		var b_y = 0.0
		var b_team = null

		if typeof(b) == TYPE_DICTIONARY:
			if "alive" in b: is_alive = b.alive
			if "ball_type" in b: b_type = b.ball_type
			if "x" in b: b_x = b.x
			if "y" in b: b_y = b.y
			if "team" in b: b_team = b.team
		elif typeof(b) == TYPE_OBJECT:
			if b.has_method("get"):
				is_alive = b.get("alive")
				b_type = b.get("ball_type")
				b_x = b.get("x")
				b_y = b.get("y")
				b_team = b.get("team")
			elif "alive" in b:
				is_alive = b.alive
				b_type = b.ball_type
				b_x = b.x
				b_y = b.y
				b_team = b.team

		if is_alive and b_type != "spectator":
			var dx = b_x - target_x
			var dy = b_y - target_y
			var dist = sqrt(dx * dx + dy * dy)
			if dist < closest_dist:
				closest_dist = dist
				winner_team = b_team

	return winner_team
