extends GameMode
func _init():
	name = "Decaying Juggernaut"
	description = "Similar to Juggernaut mode, but the Juggernaut's stats slowly decay over time, pushing players to stay aggressive and preventing endless stalling."

func setup(world, balls: Array) -> void:
	super.setup(world, balls)
	if world != null and "tick_timer" in world:
	if not "dead_balls" in world:
		world.set_meta("dead_balls", []) if world.has_method("set_meta") else null

	var valid_balls = []
	for b in balls:
		if b.ball_type != "spectator":
			valid_balls.append(b)

	if valid_balls.size() > 0:
		var boss = valid_balls[0]
		_make_juggernaut(world, boss)

		for i in range(1, valid_balls.size()):
			valid_balls[i].team = "Hunters"
			if typeof(valid_balls[i]) == TYPE_DICTIONARY:
				if not valid_balls[i].has("base_max_hp"):
					valid_balls[i]["base_max_hp"] = float(valid_balls[i].get("max_hp", 100.0))
				valid_balls[i]["max_hp"] = valid_balls[i]["base_max_hp"] * 0.8
				valid_balls[i]["hp"] = valid_balls[i]["max_hp"]
			else:
				if not valid_balls[i].has_meta("base_max_hp"):
					valid_balls[i].set_meta("base_max_hp", valid_balls[i].max_hp if "max_hp" in valid_balls[i] else 100.0)
				if "max_hp" in valid_balls[i]:
					valid_balls[i].max_hp = valid_balls[i].get_meta("base_max_hp") * 0.8
					valid_balls[i].hp = valid_balls[i].max_hp

func _make_juggernaut(world, b) -> void:
	b.team = "Juggernaut"
	if typeof(b) == TYPE_DICTIONARY:
		if not b.has("base_max_hp"):
			b["base_max_hp"] = float(b.get("max_hp", 100.0))
		b["max_hp"] = b["base_max_hp"] * 10.0
		b["hp"] = b["max_hp"]

		if not b.has("base_damage"):
			b["base_damage"] = float(b.get("damage", 10.0))
		b["damage"] = b["base_damage"] * 2.0

		if not b.has("base_radius"):
			b["base_radius"] = float(b.get("radius", 10.0))
		b["radius"] = b["base_radius"] * 3.0

		if b.has("base_speed"):
			b["base_speed"] = float(b["base_speed"]) * 0.6

		if not b.has("base_mass"):
			b["base_mass"] = float(b.get("mass", 1.0))
		b["mass"] = b["base_mass"] * 5.0

		b["juggernaut_decay"] = 1.0
	else:
		if not b.has_meta("base_max_hp"):
			b.set_meta("base_max_hp", b.max_hp if "max_hp" in b else 100.0)
		if "max_hp" in b:
			b.max_hp = b.get_meta("base_max_hp") * 10.0
			if "hp" in b:
				b.hp = b.max_hp

		if not b.has_meta("base_damage"):
			b.set_meta("base_damage", b.damage if "damage" in b else 10.0)
		if "damage" in b:
			b.damage = b.get_meta("base_damage") * 2.0

		if not b.has_meta("base_radius"):
			var cur_r = b.radius if "radius" in b else (b.get_meta("radius") if b.has_method("has_meta") and b.has_meta("radius") else 10.0)
			b.set_meta("base_radius", cur_r)
		if "radius" in b:
			b.radius = b.get_meta("base_radius") * 3.0
		elif b.has_method("has_meta") and b.has_meta("radius"):
			b.set_meta("radius", b.get_meta("base_radius") * 3.0)
		elif b.has_method("set_meta"):
			b.set_meta("radius", b.get_meta("base_radius") * 3.0)

		if "base_speed" in b:
			b.base_speed *= 0.6
		elif b.has_method("has_meta") and b.has_meta("base_speed"):
			b.set_meta("base_speed", b.get_meta("base_speed") * 0.6)

		if not b.has_meta("base_mass"):
			var cur_m = b.mass if "mass" in b else (b.get_meta("mass") if b.has_method("has_meta") and b.has_meta("mass") else 1.0)
			b.set_meta("base_mass", cur_m)
		if "mass" in b:
			b.mass = b.get_meta("base_mass") * 5.0
		elif b.has_method("has_meta") and b.has_meta("mass"):
			b.set_meta("mass", b.get_meta("base_mass") * 5.0)

		b.set_meta("juggernaut_decay", 1.0)

func tick(world, balls: Array, delta: float = 0.016) -> void:
	super.tick(world, balls, delta)

	var dead_juggernauts = []
	for b in balls:
		if "team" in b and b.team == "Juggernaut" and not b.alive:
			dead_juggernauts.append(b)

	for dead_jug in dead_juggernauts:
		var killer_id = dead_jug.killer if "killer" in dead_jug else null
		if killer_id != null:
			var killer = null
			for b in balls:
				if "id" in b and b.id == killer_id:
					killer = b
					break
			if killer != null and killer.alive:
				_make_juggernaut(world, killer)
				if world != null and world.has_method("add_event"):
					world.add_event("juggernaut_change", {"message": "A new Juggernaut has emerged!"})
		dead_jug.team = "Dead"

	for b in balls:
		if "team" in b and b.team == "Juggernaut" and b.alive:
			if "hp" in b and "max_hp" in b:
				b.hp = min(b.hp + 5.0 * delta, b.max_hp)

			var decay_rate = 0.02 # 2% per second
			var decay = 1.0

			if typeof(b) == TYPE_DICTIONARY:
				if not b.has("juggernaut_decay"):
					b["juggernaut_decay"] = 1.0
				decay = b["juggernaut_decay"]

				decay -= decay_rate * delta
				decay = max(0.2, decay)
				b["juggernaut_decay"] = decay

				if b.has("base_max_hp"):
					b["max_hp"] = b["base_max_hp"] * (1.0 + 9.0 * decay)
					b["hp"] = min(b["hp"], b["max_hp"])
				if b.has("base_damage"):
					b["damage"] = b["base_damage"] * (1.0 + 1.0 * decay)
				if b.has("base_radius"):
					b["radius"] = b["base_radius"] * (1.0 + 2.0 * decay)
				if b.has("base_mass"):
					b["mass"] = b["base_mass"] * (1.0 + 4.0 * decay)
			else:
				if not b.has_meta("juggernaut_decay"):
					b.set_meta("juggernaut_decay", 1.0)
				decay = b.get_meta("juggernaut_decay")

				decay -= decay_rate * delta
				decay = max(0.2, decay)
				b.set_meta("juggernaut_decay", decay)

				if b.has_meta("base_max_hp") and "max_hp" in b:
					b.max_hp = b.get_meta("base_max_hp") * (1.0 + 9.0 * decay)
					if "hp" in b: b.hp = min(b.hp, b.max_hp)
				if b.has_meta("base_damage") and "damage" in b:
					b.damage = b.get_meta("base_damage") * (1.0 + 1.0 * decay)
				if b.has_meta("base_radius") and "radius" in b:
					b.radius = b.get_meta("base_radius") * (1.0 + 2.0 * decay)
				if b.has_meta("base_mass") and "mass" in b:
					b.mass = b.get_meta("base_mass") * (1.0 + 4.0 * decay)

func check_winner(world, balls: Array):
	var alive = []
	for b in balls:
		if b.alive and b.ball_type != "spectator" and b.ball_type != "shadow_monster":
			alive.append(b)

	if alive.size() == 0:
		return "Draw"

	var juggernaut_alive = false
	var hunters_alive = false

	for b in alive:
		if "team" in b and b.team == "Juggernaut":
			juggernaut_alive = true
		elif "team" in b and b.team == "Hunters":
			hunters_alive = true

	if not juggernaut_alive:
		return "Hunters"
	if not hunters_alive:
		return "Juggernaut"

	return null
