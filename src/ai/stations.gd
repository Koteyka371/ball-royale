extends "res://src/ai/game_modes.gd".GameMode

var stations = []

func _init().():
	name = "Weather Stations"
	description = "Add capture-able weather stations in the arena that let a team control the weather in their sector."

func setup(world, balls):
	.setup(world, balls)

	var arena_w = 1000
	var arena_h = 1000
	if world != null:
		if typeof(world) == TYPE_DICTIONARY and "arena" in world:
			var arena = world.get("arena")
			if typeof(arena) == TYPE_DICTIONARY:
				arena_w = arena.get("width", 1000)
				arena_h = arena.get("height", 1000)
			elif arena != null:
				if "width" in arena: arena_w = arena.width
				if "height" in arena: arena_h = arena.height
		elif typeof(world) != TYPE_DICTIONARY and "arena" in world and world.arena != null:
			if typeof(world.arena) == TYPE_DICTIONARY:
				arena_w = world.arena.get("width", 1000)
				arena_h = world.arena.get("height", 1000)
			else:
				if "width" in world.arena: arena_w = world.arena.width
				if "height" in world.arena: arena_h = world.arena.height

	stations = [
		{"x": arena_w * 0.25, "y": arena_h * 0.25, "radius": 150.0, "capture_progress": 0.0, "weather": "heatwave", "owner": null},
		{"x": arena_w * 0.75, "y": arena_h * 0.25, "radius": 150.0, "capture_progress": 0.0, "weather": "blizzard", "owner": null},
		{"x": arena_w * 0.25, "y": arena_h * 0.75, "radius": 150.0, "capture_progress": 0.0, "weather": "acid_rain", "owner": null},
		{"x": arena_w * 0.75, "y": arena_h * 0.75, "radius": 150.0, "capture_progress": 0.0, "weather": "wind", "owner": null}
	]

	for b in balls:
		var b_type = ""
		if typeof(b) == TYPE_DICTIONARY:
			b_type = b.get("ball_type", "")
			if b_type != "spectator" and not b.has("team"):
				b["team"] = b_type
		else:
			if "ball_type" in b: b_type = b.ball_type
			if b_type != "spectator" and not "team" in b:
				if "team" in b:
					b.team = b_type
				elif b.has_method("set_meta"):
					b.set_meta("team", b_type)

func tick(world, balls, delta = 0.016):
	.tick(world, balls, delta)

	# Update capture progress
	for station in stations:
		var station_cx = station["x"]
		var station_cy = station["y"]
		var r = station["radius"]
		var r_sq = r * r

		var inside_balls = []
		for b in balls:
			var alive = false
			var b_type = ""
			var bx = 0.0
			var by = 0.0

			if typeof(b) == TYPE_DICTIONARY:
				alive = b.get("alive", false)
				b_type = b.get("ball_type", "")
				bx = b.get("x", 0.0)
				by = b.get("y", 0.0)
			else:
				if "alive" in b: alive = b.alive
				if "ball_type" in b: b_type = b.ball_type
				if "x" in b: bx = b.x
				if "y" in b: by = b.y

			if not alive or b_type == "spectator":
				continue

			var dx = bx - station_cx
			var dy = by - station_cy
			if dx * dx + dy * dy <= r_sq:
				inside_balls.append(b)

		if inside_balls.size() > 0:
			var teams_inside = {}
			for b in inside_balls:
				var t = "unknown"
				if typeof(b) == TYPE_DICTIONARY:
					t = b.get("team", b.get("ball_type", "unknown"))
				else:
					if "team" in b:
						t = b.team
					elif b.has_method("get_meta") and b.has_meta("team"):
						t = b.get_meta("team")
					elif "ball_type" in b:
						t = b.ball_type
				teams_inside[t] = true

			if teams_inside.size() == 1:
				var max_team = teams_inside.keys()[0]
				if station["owner"] == max_team:
					if station["capture_progress"] < 100.0:
						station["capture_progress"] = min(100.0, station["capture_progress"] + 20.0 * delta)
				else:
					station["capture_progress"] -= 20.0 * delta
					if station["capture_progress"] <= 0:
						station["owner"] = max_team
						station["capture_progress"] = 0.0
			else:
				# Contested, no progress change
				pass
		else:
			# Decay
			station["capture_progress"] = max(0.0, station["capture_progress"] - 10.0 * delta)
			if station["capture_progress"] == 0.0:
				station["owner"] = null

	# Apply weather effects
	for b in balls:
		var alive = false
		var b_type = ""
		var bx = 0.0
		var by = 0.0

		if typeof(b) == TYPE_DICTIONARY:
			alive = b.get("alive", false)
			b_type = b.get("ball_type", "")
			bx = b.get("x", 0.0)
			by = b.get("y", 0.0)
		else:
			if "alive" in b: alive = b.alive
			if "ball_type" in b: b_type = b.ball_type
			if "x" in b: bx = b.x
			if "y" in b: by = b.y

		if not alive or b_type == "spectator":
			continue

		var closest_station = null
		var min_dist_sq = 999999999.0
		for station in stations:
			var dx = bx - station["x"]
			var dy = by - station["y"]
			var dist_sq = dx * dx + dy * dy
			if dist_sq < min_dist_sq:
				min_dist_sq = dist_sq
				closest_station = station

		var base_speed = 100.0
		var base_damage = 10.0
		var team = "unknown"
		var hp = 100.0
		var max_hp = 100.0

		if typeof(b) == TYPE_DICTIONARY:
			base_speed = b.get("base_speed", 100.0)
			base_damage = b.get("base_damage", 10.0)
			team = b.get("team", b.get("ball_type", "unknown"))
			hp = b.get("hp", 100.0)
			max_hp = b.get("max_hp", 100.0)
		else:
			if "base_speed" in b: base_speed = b.base_speed
			if "base_damage" in b: base_damage = b.base_damage
			if "team" in b:
				team = b.team
			elif b.has_method("get_meta") and b.has_meta("team"):
				team = b.get_meta("team")
			elif "ball_type" in b:
				team = b.ball_type
			if "hp" in b: hp = b.hp
			if "max_hp" in b: max_hp = b.max_hp

		if closest_station != null and closest_station["capture_progress"] == 100.0:
			var is_winner = closest_station["owner"] == team
			var weather = closest_station["weather"]

			if is_winner:
				if weather == "heatwave":
					if typeof(b) == TYPE_DICTIONARY:
						b["speed"] = base_speed * 1.2
						b["damage"] = base_damage * 1.5
					else:
						if "speed" in b: b.speed = base_speed * 1.2
						if "damage" in b: b.damage = base_damage * 1.5
				elif weather == "blizzard":
					if typeof(b) == TYPE_DICTIONARY:
						b["speed"] = base_speed * 1.5
						b["damage"] = base_damage * 1.2
					else:
						if "speed" in b: b.speed = base_speed * 1.5
						if "damage" in b: b.damage = base_damage * 1.2
				elif weather == "acid_rain":
					if typeof(b) == TYPE_DICTIONARY:
						b["speed"] = base_speed * 1.2
						b["damage"] = base_damage * 1.2
						b["hp"] = min(max_hp, hp + 2.0 * delta)
					else:
						if "speed" in b: b.speed = base_speed * 1.2
						if "damage" in b: b.damage = base_damage * 1.2
						if "hp" in b: b.hp = min(max_hp, hp + 2.0 * delta)
				elif weather == "wind":
					if typeof(b) == TYPE_DICTIONARY:
						b["speed"] = base_speed * 2.0
						b["damage"] = base_damage * 1.0
					else:
						if "speed" in b: b.speed = base_speed * 2.0
						if "damage" in b: b.damage = base_damage * 1.0
				else:
					if typeof(b) == TYPE_DICTIONARY:
						b["speed"] = base_speed
						b["damage"] = base_damage
					else:
						if "speed" in b: b.speed = base_speed
						if "damage" in b: b.damage = base_damage
			else:
				if weather == "heatwave":
					if typeof(b) == TYPE_DICTIONARY:
						b["speed"] = base_speed * 0.8
						b["damage"] = base_damage * 1.0
					else:
						if "speed" in b: b.speed = base_speed * 0.8
						if "damage" in b: b.damage = base_damage * 1.0
				elif weather == "blizzard":
					if typeof(b) == TYPE_DICTIONARY:
						b["speed"] = base_speed * 1.0
						b["damage"] = base_damage * 0.8
					else:
						if "speed" in b: b.speed = base_speed * 1.0
						if "damage" in b: b.damage = base_damage * 0.8
				elif weather == "acid_rain":
					if typeof(b) == TYPE_DICTIONARY:
						b["speed"] = base_speed * 0.9
						b["damage"] = base_damage * 0.9
						b["hp"] = hp - 2.0 * delta
					else:
						if "speed" in b: b.speed = base_speed * 0.9
						if "damage" in b: b.damage = base_damage * 0.9
						if "hp" in b: b.hp = hp - 2.0 * delta
				elif weather == "wind":
					if typeof(b) == TYPE_DICTIONARY:
						b["speed"] = base_speed * 0.5
						b["damage"] = base_damage * 0.8
					else:
						if "speed" in b: b.speed = base_speed * 0.5
						if "damage" in b: b.damage = base_damage * 0.8
				else:
					if typeof(b) == TYPE_DICTIONARY:
						b["speed"] = base_speed
						b["damage"] = base_damage
					else:
						if "speed" in b: b.speed = base_speed
						if "damage" in b: b.damage = base_damage
		else:
			if typeof(b) == TYPE_DICTIONARY:
				b["speed"] = base_speed
				b["damage"] = base_damage
			else:
				if "speed" in b: b.speed = base_speed
				if "damage" in b: b.damage = base_damage

# Register logic to add this to the global GAME_MODES dictionary when loaded
var _init_game_mode = true

func _ready():
	# If this is somehow loaded into the tree
	pass
