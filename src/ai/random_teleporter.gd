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

		if randf() < 0.3:
			var p_x1 = randf_range(50.0, max(50.0, arena_w - 50.0))
			var p_y1 = randf_range(50.0, max(50.0, arena_h - 50.0))
			var p_x2 = randf_range(50.0, max(50.0, arena_w - 50.0))
			var p_y2 = randf_range(50.0, max(50.0, arena_h - 50.0))
			var p1 = {
				"x": p_x1,
				"y": p_y1,
				"radius": 30.0,
				"lifetime": 10.0,
				"cooldown": 0.0
			}
			var p2 = {
				"x": p_x2,
				"y": p_y2,
				"radius": 30.0,
				"lifetime": 10.0,
				"cooldown": 0.0
			}
			p1["link"] = p2
			p2["link"] = p1
			portals.append(p1)
			portals.append(p2)

			if typeof(world) == TYPE_DICTIONARY and world.has("add_event"):
				pass
			elif typeof(world) != TYPE_DICTIONARY and world.has_method("add_event"):
				world.add_event("portal_spawn", {"message": "A linked random teleporter portal pair appeared!", "x": p_x1, "y": p_y1})
		else:
			var p_x = randf_range(50.0, max(50.0, arena_w - 50.0))
			var p_y = randf_range(50.0, max(50.0, arena_h - 50.0))
			var portal = {
				"x": p_x,
				"y": p_y,
				"radius": 30.0,
				"lifetime": 10.0,
				"cooldown": 0.0
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
		if portal.has("cooldown") and portal["cooldown"] > 0:
			portal["cooldown"] -= delta
			continue

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
					if typeof(world) != TYPE_DICTIONARY and world.has_method("add_event"):
						world.add_event("teleport_out", {"message": "Teleported!", "x": bx, "y": by})

					var dest_x = 0.0
					var dest_y = 0.0

					if portal.has("link"):
						var linked = portal["link"]
						dest_x = linked["x"]
						dest_y = linked["y"]

						if typeof(b) == TYPE_DICTIONARY:
							b["x"] = dest_x
							b["y"] = dest_y
						else:
							if "x" in b: b.x = dest_x
							if "y" in b: b.y = dest_y

						portal["cooldown"] = 0.5
						linked["cooldown"] = 0.5
					else:
						dest_x = randf_range(50.0, max(50.0, arena_w - 50.0))
						dest_y = randf_range(50.0, max(50.0, arena_h - 50.0))

						if typeof(b) == TYPE_DICTIONARY:
							b["x"] = dest_x
							b["y"] = dest_y
							b["vx"] = 0.0
							b["vy"] = 0.0
						else:
							if "x" in b: b.x = dest_x
							if "y" in b: b.y = dest_y
							if "vx" in b: b.vx = 0.0
							if "vy" in b: b.vy = 0.0

						portal["cooldown"] = 0.5

					if typeof(world) != TYPE_DICTIONARY and world.has_method("add_event"):
						world.add_event("teleport_in", {"message": "Arrived!", "x": dest_x, "y": dest_y})

					break
