<<<<<<< SEARCH
	"massive_black_hole_event": MassiveBlackHoleEventMode.new(),
	"ticking_bomb": TickingBombMode.new(),
}


class CrossfireMode extends GameMode:
=======
	"massive_black_hole_event": MassiveBlackHoleEventMode.new(),
	"ticking_bomb": TickingBombMode.new(),
	"orbital_mines": OrbitalMinesMode.new(),
}


class OrbitalMinesMode extends GameMode:
	var orbit_speed: float = 1.0 # radians per second
	var orbit_distance: float = 300.0
	var rng: RandomNumberGenerator = RandomNumberGenerator.new()

	func _init():
		super()
		name = "Orbital Mines"
		description = "Orbital mines constantly revolve around the center of the arena."
		rng.randomize()

	func tick(world, balls: Array, delta: float = 0.016) -> void:
		.tick(world, balls, delta)
		if typeof(world) != TYPE_OBJECT or not ("arena" in world) or not ("hazards" in world.arena):
			return

		var cx = 500.0
		var cy = 500.0
		if "width" in world:
			cx = world.width / 2.0
		elif "width" in world.arena:
			cx = world.arena.width / 2.0
		if "height" in world:
			cy = world.height / 2.0
		elif "height" in world.arena:
			cy = world.arena.height / 2.0

		var mines = []
		for h in world.arena.hazards:
			if typeof(h) == TYPE_OBJECT and h.get("kind") == "orbital_mine":
				mines.append(h)
			elif typeof(h) == TYPE_DICTIONARY and h.get("kind") == "orbital_mine":
				mines.append(h)

		if mines.size() < 5:
			var HazardObj = load("res://src/arena/procedural_arena.gd")
			if HazardObj != null:
				HazardObj = HazardObj.Hazard
				var num_to_spawn = 5 - mines.size()
				for i in range(num_to_spawn):
					var mine_id = world.arena.hazards.size() + rng.randi_range(10000, 99999)
					var mine = HazardObj.new(mine_id, cx, cy, "orbital_mine", 20.0)
					if "damage" in mine: mine.damage = 30.0
					if mine.has_method("set_meta"):
						mine.set_meta("active", true)
						mine.set_meta("duration", 9999.0)
						mine.set_meta("angle", rng.randf_range(0, 2 * PI))
						mine.set_meta("orbit_dist", rng.randf_range(150.0, 450.0))
						var mult = rng.randf_range(0.8, 1.5)
						if rng.randi() % 2 == 0: mult = -mult
						mine.set_meta("speed_mult", mult)
					world.arena.hazards.append(mine)
					mines.append(mine)

		for m in mines:
			var is_active = true
			if typeof(m) == TYPE_OBJECT and m.has_method("has_meta") and m.has_meta("active"):
				is_active = m.get_meta("active")
			elif typeof(m) == TYPE_DICTIONARY and m.has("active"):
				is_active = m.get("active")

			if is_active:
				var ang = 0.0
				var mult = 1.0
				var dist = orbit_distance
				if typeof(m) == TYPE_OBJECT and m.has_method("get_meta"):
					ang = m.get_meta("angle")
					mult = m.get_meta("speed_mult")
					dist = m.get_meta("orbit_dist")
				elif typeof(m) == TYPE_DICTIONARY:
					ang = m.get("angle") if m.has("angle") else 0.0
					mult = m.get("speed_mult") if m.has("speed_mult") else 1.0
					dist = m.get("orbit_dist") if m.has("orbit_dist") else orbit_distance

				var spd = orbit_speed * mult
				ang += spd * delta

				var nx = cx + cos(ang) * dist
				var ny = cy + sin(ang) * dist

				if typeof(m) == TYPE_OBJECT:
					if m.has_method("set_meta"):
						m.set_meta("angle", ang)
					if "x" in m: m.x = nx
					if "y" in m: m.y = ny
				elif typeof(m) == TYPE_DICTIONARY:
					m["angle"] = ang
					m["x"] = nx
					m["y"] = ny


class CrossfireMode extends GameMode:
>>>>>>> REPLACE
