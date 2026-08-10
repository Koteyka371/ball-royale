extends "res://src/ai/game_modes.gd".GameMode

var portals = []
var teleport_timer = 0.0
var teleport_interval = 20.0
var max_portals = 4

func _init():
	super._init()
	name = "Random Portals"
	description = "Portals appear across the map. Balls entering a portal exit immediately from a random other portal, maintaining their velocity. The portals change locations every 20 seconds."

func setup(world, balls):
	super.setup(world, balls)
	teleport_timer = 0.0
	_spawn_portals(world)

func _spawn_portals(world):
	portals = []
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
	for i in range(max_portals):
		var portal = {
			"x": randf_range(100.0, max(100.0, arena_w - 100.0)),
			"y": randf_range(100.0, max(100.0, arena_h - 100.0)),
			"radius": 40.0,
			"cooldown": 0.0
		}
		portals.append(portal)
	if typeof(world) != TYPE_DICTIONARY and world.has_method("add_event"):
		world.add_event("random_portals_spawn", {"message": "New portals have appeared!"})

func tick(world, balls, delta = 0.016):
	super.tick(world, balls, delta)

	if portals.size() == 0:
		_spawn_portals(world)

	teleport_timer += delta
	if teleport_timer >= teleport_interval:
		teleport_timer -= teleport_interval
		_spawn_portals(world)

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
					var other_portals = []
					for p in portals:
						if p != portal:
							other_portals.append(p)
					if other_portals.size() > 0:
						var target_portal = other_portals[randi() % other_portals.size()]

						var vx = 0.0
						var vy = 0.0
						if typeof(b) == TYPE_DICTIONARY:
							vx = b.get("vx", 0.0)
							vy = b.get("vy", 0.0)
						else:
							if "vx" in b: vx = b.vx
							if "vy" in b: vy = b.vy

						if vx == 0.0 and vy == 0.0:
							vx = 1.0
							vy = 0.0

						var v_len = sqrt(vx * vx + vy * vy)
						var nx = vx / v_len
						var ny = vy / v_len

						var offset = target_portal["radius"] + br + 5.0
						var target_x = target_portal["x"] + nx * offset
						var target_y = target_portal["y"] + ny * offset

						if typeof(b) == TYPE_DICTIONARY:
							b["x"] = target_x
							b["y"] = target_y
						else:
							if "x" in b: b.x = target_x
							if "y" in b: b.y = target_y

						if typeof(world) != TYPE_DICTIONARY and world.has_method("add_event"):
							world.add_event("random_portal_teleport", {"x": target_portal["x"], "y": target_portal["y"]})
					break
