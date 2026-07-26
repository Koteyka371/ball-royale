extends Node

var name: String = "Guild Wars Base Building"
var description: String = "Customize HQ and attack opposing guild bases."
var hq_hp: float = 10000.0
var defenses: Array = []

func setup(world, balls: Array) -> void:
	if world == null or not world.has("arena"):
		return

	if typeof(world.arena) == TYPE_DICTIONARY:
		if not world.arena.has("hq"):
			world.arena.hq = {
				"x": 0.0,
				"y": 0.0,
				"radius": 100.0,
				"hp": self.hq_hp,
				"max_hp": self.hq_hp,
				"team": "defender"
			}
		self.defenses = [
			{"type": "turret", "x": 100.0, "y": 100.0, "damage": 50.0, "range": 300.0, "team": "defender"},
			{"type": "wall", "x": -100.0, "y": 0.0, "width": 50.0, "height": 200.0, "hp": 1000.0, "team": "defender"},
			{"type": "trap", "x": 0.0, "y": 200.0, "damage": 100.0, "radius": 40.0, "team": "defender"}
		]
		world.arena.defenses = self.defenses
	elif typeof(world.arena) == TYPE_OBJECT:
		if not world.arena.has("hq"):
			world.arena.set("hq", {
				"x": 0.0,
				"y": 0.0,
				"radius": 100.0,
				"hp": self.hq_hp,
				"max_hp": self.hq_hp,
				"team": "defender"
			})
		self.defenses = [
			{"type": "turret", "x": 100.0, "y": 100.0, "damage": 50.0, "range": 300.0, "team": "defender"},
			{"type": "wall", "x": -100.0, "y": 0.0, "width": 50.0, "height": 200.0, "hp": 1000.0, "team": "defender"},
			{"type": "trap", "x": 0.0, "y": 200.0, "damage": 100.0, "radius": 40.0, "team": "defender"}
		]
		world.arena.set("defenses", self.defenses)

func tick(world, balls: Array, delta: float = 0.016) -> void:
	if world == null or not world.has("arena"):
		return

	var arena = world.get("arena") if typeof(world) == TYPE_OBJECT else world.arena

	var has_hq = false
	var has_defenses = false
	if typeof(arena) == TYPE_DICTIONARY:
		has_hq = arena.has("hq")
		has_defenses = arena.has("defenses")
	elif typeof(arena) == TYPE_OBJECT:
		has_hq = arena.get("hq") != null
		has_defenses = arena.get("defenses") != null

	if not has_hq or not has_defenses:
		return

	var hq = arena.get("hq") if typeof(arena) == TYPE_OBJECT else arena.hq
	var arena_defenses = arena.get("defenses") if typeof(arena) == TYPE_OBJECT else arena.defenses

	for b in balls:
		var is_alive = true
		if typeof(b) == TYPE_DICTIONARY:
			is_alive = b.get("alive", true)
		elif typeof(b) == TYPE_OBJECT:
			is_alive = b.get("alive") if b.has_method("get") and b.get("alive") != null else true

		if not is_alive:
			continue

		var b_team = b.get("team") if typeof(b) == TYPE_OBJECT else b.get("team")
		var b_x = b.get("x") if typeof(b) == TYPE_OBJECT else b.get("x", 0.0)
		var b_y = b.get("y") if typeof(b) == TYPE_OBJECT else b.get("y", 0.0)
		var b_radius = b.get("radius") if typeof(b) == TYPE_OBJECT else b.get("radius", 20.0)
		var b_damage = b.get("damage") if typeof(b) == TYPE_OBJECT else b.get("damage", 10.0)

		if b_team != hq.team:
			var dx = b_x - hq.x
			var dy = b_y - hq.y
			var dist = sqrt(dx*dx + dy*dy)

			if dist < hq.radius + b_radius:
				hq.hp -= b_damage * delta
				if hq.hp < 0:
					hq.hp = 0

		for defense in arena_defenses:
			if defense.team != b_team:
				if defense.type == "turret":
					var dx = b_x - defense.x
					var dy = b_y - defense.y
					var dist = sqrt(dx*dx + dy*dy)
					if dist < defense.range:
						if typeof(b) == TYPE_DICTIONARY and b.has("hp"):
							b.hp -= defense.damage * delta
						elif typeof(b) == TYPE_OBJECT and b.has_method("get") and b.get("hp") != null:
							b.set("hp", b.get("hp") - defense.damage * delta)
				elif defense.type == "trap":
					var dx = b_x - defense.x
					var dy = b_y - defense.y
					var dist = sqrt(dx*dx + dy*dy)
					if dist < defense.radius + b_radius:
						if typeof(b) == TYPE_DICTIONARY and b.has("hp"):
							b.hp -= defense.damage
						elif typeof(b) == TYPE_OBJECT and b.has_method("get") and b.get("hp") != null:
							b.set("hp", b.get("hp") - defense.damage)
						defense.type = "used_trap"
				elif defense.type == "wall":
					pass
