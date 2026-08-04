extends Node

const GameMode = preload("res://src/ai/game_modes.gd").GameMode

class MirrorWorldMode extends GameMode:
	var mirror_timer: float = 0.0
	var is_mirrored: bool = false
	var mirror_duration: float = 5.0
	var normal_duration: float = 10.0
	var shadows: Array = []

	func _init():
		name = "Mirror World"
		description = "Creates a temporary mirror version of the map."

	func tick(world: Dictionary, balls: Array, delta: float = 0.016):
		super.tick(world, balls, delta)
		mirror_timer += delta

		if not is_mirrored and mirror_timer >= normal_duration:
			is_mirrored = true
			mirror_timer = 0.0
			_mirror_world(world, balls)
			_spawn_shadows(world, balls)
		elif is_mirrored and mirror_timer >= mirror_duration:
			is_mirrored = false
			mirror_timer = 0.0
			_mirror_world(world, balls)
			_remove_shadows(world, balls)

		if is_mirrored:
			_update_shadows(world, balls)

	func _spawn_shadows(world: Dictionary, balls: Array):
		var arena_width = 1000.0
		if world.has("arena") and world.arena != null:
			if typeof(world.arena) == TYPE_DICTIONARY and world.arena.has("width"):
				arena_width = float(world.arena.width)
			elif typeof(world.arena) == TYPE_OBJECT and "width" in world.arena:
				arena_width = float(world.arena.width)

		var center_x = arena_width / 2.0

		for b in balls:
			var b_alive = true
			var b_is_clone = false
			if typeof(b) == TYPE_DICTIONARY:
				b_alive = b.get("alive", true)
				b_is_clone = b.get("is_clone", false)
			elif typeof(b) == TYPE_OBJECT:
				b_alive = b.alive if "alive" in b else true
				b_is_clone = b.is_clone if "is_clone" in b else false

			if not b_alive or b_is_clone:
				continue

			var b_id = 0
			var b_x = 0.0
			var b_y = 0.0
			var b_vx = 0.0
			var b_vy = 0.0
			var b_radius = 15.0
			var b_hp = 100.0
			var b_max_hp = 100.0
			var b_team = ""

			if typeof(b) == TYPE_DICTIONARY:
				b_id = b.get("id", randi())
				b_x = b.get("x", 0.0)
				b_y = b.get("y", 0.0)
				b_vx = b.get("vx", 0.0)
				b_vy = b.get("vy", 0.0)
				b_radius = b.get("radius", 15.0)
				b_hp = b.get("hp", 100.0)
				b_max_hp = b.get("max_hp", 100.0)
				b_team = b.get("team", "")
			elif typeof(b) == TYPE_OBJECT:
				b_id = b.get("id") if b.has_method("get") and "id" in b else randi()
				b_x = b.x if "x" in b else 0.0
				b_y = b.y if "y" in b else 0.0
				b_vx = b.vx if "vx" in b else 0.0
				b_vy = b.vy if "vy" in b else 0.0
				b_radius = b.radius if "radius" in b else 15.0
				b_hp = b.hp if "hp" in b else 100.0
				b_max_hp = b.max_hp if "max_hp" in b else 100.0
				b_team = b.team if "team" in b else ""

			var shadow = {
				"id": b_id + 900000,
				"owner": b,
				"x": center_x + (center_x - b_x),
				"y": b_y,
				"vx": -b_vx,
				"vy": b_vy,
				"radius": b_radius,
				"hp": b_hp,
				"max_hp": b_max_hp,
				"last_hp": b_hp,
				"alive": true,
				"is_clone": true,
				"is_mirror_shadow": true,
				"team": b_team,
				"color": "black"
			}
			shadows.append(shadow)
			if world.has("balls"):
				world.balls.append(shadow)

	func _update_shadows(world: Dictionary, balls: Array):
		var arena_width = 1000.0
		if world.has("arena") and world.arena != null:
			if typeof(world.arena) == TYPE_DICTIONARY and world.arena.has("width"):
				arena_width = float(world.arena.width)
			elif typeof(world.arena) == TYPE_OBJECT and "width" in world.arena:
				arena_width = float(world.arena.width)

		var center_x = arena_width / 2.0

		for s in shadows:
			var owner = s["owner"]
			var o_alive = true
			if typeof(owner) == TYPE_DICTIONARY:
				o_alive = owner.get("alive", true)
			elif typeof(owner) == TYPE_OBJECT:
				o_alive = owner.alive if "alive" in owner else true

			if not s["alive"] or not o_alive:
				s["alive"] = false
				continue

			var o_x = 0.0
			var o_y = 0.0
			var o_vx = 0.0
			var o_vy = 0.0
			var o_hp = 100.0
			var o_max_hp = 100.0

			if typeof(owner) == TYPE_DICTIONARY:
				o_x = owner.get("x", 0.0)
				o_y = owner.get("y", 0.0)
				o_vx = owner.get("vx", 0.0)
				o_vy = owner.get("vy", 0.0)
				o_hp = owner.get("hp", 100.0)
				o_max_hp = owner.get("max_hp", 100.0)
			elif typeof(owner) == TYPE_OBJECT:
				o_x = owner.x if "x" in owner else 0.0
				o_y = owner.y if "y" in owner else 0.0
				o_vx = owner.vx if "vx" in owner else 0.0
				o_vy = owner.vy if "vy" in owner else 0.0
				o_hp = owner.hp if "hp" in owner else 100.0
				o_max_hp = owner.max_hp if "max_hp" in owner else 100.0

			s["x"] = center_x + (center_x - o_x)
			s["y"] = o_y
			s["vx"] = -o_vx
			s["vy"] = o_vy

			if s["hp"] < s["last_hp"]:
				var damage = s["last_hp"] - s["hp"]
				var new_hp = max(0.0, o_hp - damage)

				if typeof(owner) == TYPE_DICTIONARY:
					owner["hp"] = new_hp
					if new_hp <= 0:
						owner["alive"] = false
				elif typeof(owner) == TYPE_OBJECT:
					if "hp" in owner: owner.hp = new_hp
					if new_hp <= 0 and "alive" in owner:
						owner.alive = false

				o_hp = new_hp

			s["hp"] = o_hp
			s["max_hp"] = o_max_hp
			s["last_hp"] = o_hp

	func _remove_shadows(world: Dictionary, balls: Array):
		for s in shadows:
			s["alive"] = false

		if world.has("balls"):
			var new_balls = []
			for b in world.balls:
				var is_mirror = false
				if typeof(b) == TYPE_DICTIONARY:
					is_mirror = b.get("is_mirror_shadow", false)
				elif typeof(b) == TYPE_OBJECT:
					is_mirror = b.is_mirror_shadow if "is_mirror_shadow" in b else false

				if not is_mirror:
					new_balls.append(b)
			world.balls = new_balls

		shadows.clear()

	func _mirror_world(world: Dictionary, balls: Array):
		var arena_width = 1000.0
		if world.has("arena") and world.arena != null:
			if typeof(world.arena) == TYPE_DICTIONARY and world.arena.has("width"):
				arena_width = float(world.arena.width)
			elif typeof(world.arena) == TYPE_OBJECT and "width" in world.arena:
				arena_width = float(world.arena.width)

		var center_x = arena_width / 2.0

		if world.has("arena") and world.arena != null:
			var hazards = []
			if typeof(world.arena) == TYPE_DICTIONARY and world.arena.has("hazards"):
				hazards = world.arena.hazards
			elif typeof(world.arena) == TYPE_OBJECT and "hazards" in world.arena:
				hazards = world.arena.hazards

			for hazard in hazards:
				if typeof(hazard) == TYPE_DICTIONARY:
					if hazard.has("x"):
						hazard.x = center_x + (center_x - hazard.x)
					if hazard.has("vx"):
						hazard.vx = -hazard.vx
				elif typeof(hazard) == TYPE_OBJECT:
					if "x" in hazard:
						hazard.x = center_x + (center_x - hazard.x)
					if "vx" in hazard:
						hazard.vx = -hazard.vx

			var boosters = []
			if typeof(world.arena) == TYPE_DICTIONARY and world.arena.has("boosters"):
				boosters = world.arena.boosters
			elif typeof(world.arena) == TYPE_OBJECT and "boosters" in world.arena:
				boosters = world.arena.boosters

			for booster in boosters:
				if typeof(booster) == TYPE_DICTIONARY:
					if booster.has("x"):
						booster.x = center_x + (center_x - booster.x)
					if booster.has("vx"):
						booster.vx = -booster.vx
				elif typeof(booster) == TYPE_OBJECT:
					if "x" in booster:
						booster.x = center_x + (center_x - booster.x)
					if "vx" in booster:
						booster.vx = -booster.vx

		if world.has("projectiles"):
			for p in world.projectiles:
				if typeof(p) == TYPE_DICTIONARY:
					if p.has("x"):
						p.x = center_x + (center_x - p.x)
					if p.has("vx"):
						p.vx = -p.vx
					if p.has("target_x"):
						p.target_x = center_x + (center_x - p.target_x)
				elif typeof(p) == TYPE_OBJECT:
					if "x" in p:
						p.x = center_x + (center_x - p.x)
					if "vx" in p:
						p.vx = -p.vx
					if "target_x" in p:
						p.target_x = center_x + (center_x - p.target_x)

		for b in balls:
			if typeof(b) == TYPE_DICTIONARY:
				if b.has("x"):
					b.x = center_x + (center_x - b.x)
				if b.has("vx"):
					b.vx = -b.vx
			elif typeof(b) == TYPE_OBJECT:
				if "x" in b:
					b.x = center_x + (center_x - b.x)
				if "vx" in b:
					b.vx = -b.vx
