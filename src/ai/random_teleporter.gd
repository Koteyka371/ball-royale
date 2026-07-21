extends "res://src/ai/game_modes.gd".GameMode

var portals = []
var spawn_timer = 0.0
var spawn_interval = 5.0

func _init():
	super._init()
	name = "Random Teleporter"
	description = "Periodically, portals randomly appear on the map and teleport balls to random locations, breaking positioning strategies."

func tick(world, balls, delta = 0.016):
	super.tick(world, balls, delta)

	var arena_w = 800.0
	var arena_h = 600.0
	if world != null:
		if typeof(world) == TYPE_DICTIONARY and "arena" in world:
			var arena = world.get("arena")
			if typeof(arena) == TYPE_DICTIONARY:
				arena_w = arena.get("width", 800.0)
				arena_h = arena.get("height", 600.0)
			elif arena != null:
				if "width" in arena: arena_w = arena.width
				if "height" in arena: arena_h = arena.height
		elif typeof(world) != TYPE_DICTIONARY and "arena" in world and world.arena != null:
			if typeof(world.arena) == TYPE_DICTIONARY:
				arena_w = world.arena.get("width", 800.0)
				arena_h = world.arena.get("height", 600.0)
			else:
				if "width" in world.arena: arena_w = world.arena.width
				if "height" in world.arena: arena_h = world.arena.height

	spawn_timer += delta
	if spawn_timer >= spawn_interval:
		spawn_timer -= spawn_interval
		var p_x = randf_range(50.0, max(50.0, arena_w - 50.0))
		var p_y = randf_range(50.0, max(50.0, arena_h - 50.0))
		var portal = {
			"x": p_x,
			"y": p_y,
			"radius": 30.0,
			"lifetime": 10.0
		}
		portals.append(portal)
		if typeof(world) == TYPE_DICTIONARY and world.has("add_event"):
			pass # Dict worlds usually don't have add_event method
		elif typeof(world) != TYPE_DICTIONARY and world.has_method("add_event"):
			world.add_event("portal_spawn", {"message": "A random teleporter portal appeared!", "x": p_x, "y": p_y})

	var active_portals = []
	for portal in portals:
		portal["lifetime"] -= delta
		if portal["lifetime"] > 0:
			active_portals.append(portal)
	portals = active_portals

	for portal in portals:
		var px = portal["x"]
		var py = portal["y"]
		var pr = portal["radius"]
		for b in balls:
			var alive = false
			var bx = 0.0
			var by = 0.0
			var br = 10.0

			if typeof(b) == TYPE_DICTIONARY:
				alive = b.get("alive", false)
				bx = b.get("x", 0.0)
				by = b.get("y", 0.0)
				br = b.get("radius", 10.0)
			else:
				if "alive" in b: alive = b.alive
				if "x" in b: bx = b.x
				if "y" in b: by = b.y
				if "radius" in b: br = b.radius

			if alive:
				var dx = bx - px
				var dy = by - py
				var dist = sqrt(dx * dx + dy * dy)
				if dist < pr + br:
					var new_x = randf_range(50.0, max(50.0, arena_w - 50.0))
					var new_y = randf_range(50.0, max(50.0, arena_h - 50.0))

					if typeof(world) != TYPE_DICTIONARY and world.has_method("add_event"):
						world.add_event("teleport_out", {"message": "Teleported!", "x": bx, "y": by})

					if typeof(b) == TYPE_DICTIONARY:
						b["x"] = new_x
						b["y"] = new_y
						b["vx"] = 0.0
						b["vy"] = 0.0
					else:
						if "x" in b: b.x = new_x
						if "y" in b: b.y = new_y
						if "vx" in b: b.vx = 0.0
						if "vy" in b: b.vy = 0.0

					if typeof(world) != TYPE_DICTIONARY and world.has_method("add_event"):
						world.add_event("teleport_in", {"message": "Arrived!", "x": new_x, "y": new_y})
