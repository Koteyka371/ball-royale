extends "res://src/ai/game_modes.gd".GameMode

var portals = []
var spawn_timer = 0.0
var spawn_interval = 4.0
var max_portals = 5

func _init():
	super._init()
	name = "Bouncy Portals"
	description = "Portals spawn on the map that reflect projectiles and players based on velocity and incidence angle, turning the arena into a bouncy chaos."

func tick(world, balls, delta = 0.016):
	super.tick(world, balls, delta)

	var arena_w = 800.0
	var arena_h = 600.0
	var hazards = []
	if world != null:
		if typeof(world) == TYPE_DICTIONARY and "arena" in world:
			var arena = world.get("arena")
			if typeof(arena) == TYPE_DICTIONARY:
				arena_w = arena.get("width", 800.0)
				arena_h = arena.get("height", 600.0)
				hazards = arena.get("hazards", [])
			elif arena != null:
				if "width" in arena: arena_w = arena.width
				if "height" in arena: arena_h = arena.height
				if "hazards" in arena: hazards = arena.hazards
		elif typeof(world) != TYPE_DICTIONARY and "arena" in world and world.arena != null:
			if typeof(world.arena) == TYPE_DICTIONARY:
				arena_w = world.arena.get("width", 800.0)
				arena_h = world.arena.get("height", 600.0)
				hazards = world.arena.get("hazards", [])
			else:
				if "width" in world.arena: arena_w = world.arena.width
				if "height" in world.arena: arena_h = world.arena.height
				if "hazards" in world.arena: hazards = world.arena.hazards

	spawn_timer += delta
	if spawn_timer >= spawn_interval and portals.size() < max_portals:
		spawn_timer -= spawn_interval

		var angle = randf_range(0.0, 2.0 * PI)
		var nx = cos(angle)
		var ny = sin(angle)

		var p_x = randf_range(100.0, max(100.0, arena_w - 100.0))
		var p_y = randf_range(100.0, max(100.0, arena_h - 100.0))
		var portal = {
			"x": p_x,
			"y": p_y,
			"radius": 40.0,
			"nx": nx,
			"ny": ny,
			"lifetime": 15.0
		}
		portals.append(portal)
		if typeof(world) != TYPE_DICTIONARY and world.has_method("add_event"):
			world.add_event("bouncy_portal_spawn", {"x": p_x, "y": p_y})

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
		var nx = portal["nx"]
		var ny = portal["ny"]

		for b in balls:
			var alive = false
			var bx = 0.0
			var by = 0.0
			var br = 10.0
			var bvx = 0.0
			var bvy = 0.0

			if typeof(b) == TYPE_DICTIONARY:
				alive = b.get("alive", false)
				bx = b.get("x", 0.0)
				by = b.get("y", 0.0)
				br = b.get("radius", 10.0)
				bvx = b.get("vx", 0.0)
				bvy = b.get("vy", 0.0)
			else:
				if "alive" in b: alive = b.alive
				if "x" in b: bx = b.x
				if "y" in b: by = b.y
				if "radius" in b: br = b.radius
				if "vx" in b: bvx = b.vx
				if "vy" in b: bvy = b.vy

			if alive:
				var dx = bx - px
				var dy = by - py
				var dist = sqrt(dx * dx + dy * dy)
				if dist < pr + br:
					var vel_dot_normal = bvx * nx + bvy * ny

					if vel_dot_normal < 0:
						var bounce_mult = 1.5
						var new_vx = bvx - 2 * vel_dot_normal * nx
						var new_vy = bvy - 2 * vel_dot_normal * ny

						var overlap = (pr + br) - dist
						var push_nx = nx
						var push_ny = ny
						if dist > 0.01:
							push_nx = dx / dist
							push_ny = dy / dist

						var final_x = bx + push_nx * overlap
						var final_y = by + push_ny * overlap
						var final_vx = new_vx * bounce_mult
						var final_vy = new_vy * bounce_mult

						if typeof(b) == TYPE_DICTIONARY:
							b["x"] = final_x
							b["y"] = final_y
							b["vx"] = final_vx
							b["vy"] = final_vy
						else:
							if "x" in b: b.x = final_x
							if "y" in b: b.y = final_y
							if "vx" in b: b.vx = final_vx
							if "vy" in b: b.vy = final_vy

						if typeof(world) != TYPE_DICTIONARY and world.has_method("add_event"):
							world.add_event("portal_bounce", {"x": px, "y": py})

		for h in hazards:
			var active = true
			var hx = 0.0
			var hy = 0.0
			var hr = 10.0
			var hvx = 0.0
			var hvy = 0.0

			if typeof(h) == TYPE_DICTIONARY:
				active = h.get("active", true)
				hx = h.get("x", 0.0)
				hy = h.get("y", 0.0)
				hr = h.get("radius", 10.0)
				hvx = h.get("vx", 0.0)
				hvy = h.get("vy", 0.0)
			else:
				if "active" in h: active = h.active
				if "x" in h: hx = h.x
				if "y" in h: hy = h.y
				if "radius" in h: hr = h.radius
				if "vx" in h: hvx = h.vx
				if "vy" in h: hvy = h.vy

			if active and (abs(hvx) > 0.1 or abs(hvy) > 0.1):
				var dx = hx - px
				var dy = hy - py
				var dist = sqrt(dx * dx + dy * dy)
				if dist < pr + hr:
					var vel_dot_normal = hvx * nx + hvy * ny

					if vel_dot_normal < 0:
						var new_vx = hvx - 2 * vel_dot_normal * nx
						var new_vy = hvy - 2 * vel_dot_normal * ny

						var overlap = (pr + hr) - dist
						var push_nx = nx
						var push_ny = ny
						if dist > 0.01:
							push_nx = dx / dist
							push_ny = dy / dist

						var final_x = hx + push_nx * overlap
						var final_y = hy + push_ny * overlap

						if typeof(h) == TYPE_DICTIONARY:
							h["x"] = final_x
							h["y"] = final_y
							h["vx"] = new_vx
							h["vy"] = new_vy
						else:
							if "x" in h: h.x = final_x
							if "y" in h: h.y = final_y
							if "vx" in h: h.vx = new_vx
							if "vy" in h: h.vy = new_vy

						if typeof(world) != TYPE_DICTIONARY and world.has_method("add_event"):
							world.add_event("portal_bounce", {"x": px, "y": py})
