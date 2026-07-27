extends "res://src/ai/game_modes.gd".GameMode

var spawn_timer = 0.0
var spawn_interval = 5.0
var fence_speed = 100.0
var fence_damage_per_second = 100.0
var fence_thickness = 20.0
var fences = []

func _init():
	super._init()
	name = "Laser Fence"
	description = "Hazard lines periodically spawn and move across the arena, damaging anyone caught."

func setup(world, balls: Array) -> void:
	super.setup(world, balls)
	spawn_timer = 0.0
	fences = []

func tick(world, balls: Array, delta: float = 0.016) -> void:
	super.tick(world, balls, delta)

	var arena_width = 1000.0
	var arena_height = 1000.0

	if world != null:
		if typeof(world) == TYPE_DICTIONARY and "arena" in world:
			if typeof(world.arena) == TYPE_DICTIONARY:
				arena_width = world.arena.get("width", 1000.0)
				arena_height = world.arena.get("height", 1000.0)
			else:
				if "width" in world.arena: arena_width = world.arena.width
				if "height" in world.arena: arena_height = world.arena.height
		elif typeof(world) == TYPE_OBJECT and "arena" in world and world.arena != null:
			if typeof(world.arena) == TYPE_DICTIONARY:
				arena_width = world.arena.get("width", 1000.0)
				arena_height = world.arena.get("height", 1000.0)
			else:
				if "width" in world.arena: arena_width = world.arena.width
				if "height" in world.arena: arena_height = world.arena.height

	spawn_timer += delta
	if spawn_timer >= spawn_interval:
		spawn_timer -= spawn_interval

		var is_horizontal = randf() > 0.5
		var orientation = "horizontal" if is_horizontal else "vertical"
		var dir = 1 if randf() > 0.5 else -1

		var pos = 0.0
		if is_horizontal:
			pos = 0.0 if dir == 1 else arena_height
		else:
			pos = 0.0 if dir == 1 else arena_width

		fences.append({
			"orientation": orientation,
			"pos": pos,
			"dir": dir
		})

	var active_fences = []
	for fence in fences:
		fence["pos"] += fence_speed * delta * fence["dir"]

		if fence["orientation"] == "horizontal":
			if fence["pos"] >= -100 and fence["pos"] <= arena_height + 100:
				active_fences.append(fence)
		else:
			if fence["pos"] >= -100 and fence["pos"] <= arena_width + 100:
				active_fences.append(fence)

	fences = active_fences

	for fence in fences:
		for b in balls:
			var alive = b.get("alive", false) if typeof(b) == TYPE_DICTIONARY else (b.alive if "alive" in b else false)
			var b_type = b.get("ball_type", "") if typeof(b) == TYPE_DICTIONARY else (b.ball_type if "ball_type" in b else "")

			if not alive or b_type == "spectator":
				continue

			var b_x = b.get("x", 0.0) if typeof(b) == TYPE_DICTIONARY else (b.x if "x" in b else 0.0)
			var b_y = b.get("y", 0.0) if typeof(b) == TYPE_DICTIONARY else (b.y if "y" in b else 0.0)

			var hit = false
			if fence["orientation"] == "horizontal":
				if abs(b_y - fence["pos"]) < fence_thickness:
					hit = true
			else:
				if abs(b_x - fence["pos"]) < fence_thickness:
					hit = true

			if hit:
				var hp = b.get("hp", 100.0) if typeof(b) == TYPE_DICTIONARY else (b.hp if "hp" in b else 100.0)
				hp -= fence_damage_per_second * delta
				if hp <= 0:
					hp = 0
					if typeof(b) == TYPE_DICTIONARY:
						b["alive"] = false
					else:
						b.alive = false

				if typeof(b) == TYPE_DICTIONARY:
					b["hp"] = hp
				else:
					b.hp = hp
