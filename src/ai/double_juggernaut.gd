extends "res://src/ai/game_modes.gd"

class DoubleJuggernautMode extends GameMode:

	var weather: String = "clear"
	var weather_timer: float = 0.0
	var altars: Array = []
	func _init():
		super._init()
		name = "Double Juggernaut"
		description = "Two players spawn as Juggernauts. When one is killed, they drop a massive heal, but the remaining Juggernaut gets an enrage buff."

	func setup(world, balls: Array) -> void:
		super.setup(world, balls)

		var arena_w = 1000.0
		var arena_h = 1000.0
		if world != null and ("arena" in world) and world.arena != null:
			if typeof(world.arena) == TYPE_DICTIONARY:
				arena_w = world.arena.get("width", 1000.0)
				arena_h = world.arena.get("height", 1000.0)
			else:
				if "width" in world.arena: arena_w = world.arena.width
				if "height" in world.arena: arena_h = world.arena.height
		altars = [{"x": arena_w/2.0, "y": arena_h/2.0, "radius": 150.0, "capture_progress": 0.0, "owner": null, "sabotaged_by": null}]

		if world != null:
			if typeof(world) == TYPE_DICTIONARY:
				if not world.has("boosters"):
					world["boosters"] = []
			elif typeof(world) == TYPE_OBJECT:
				if not "boosters" in world:
					if world.has_method("set_meta"):
						world.set_meta("boosters", [])

		var valid_balls = []
		for b in balls:
			var b_type = b.get("ball_type") if typeof(b) == TYPE_DICTIONARY else (b.ball_type if "ball_type" in b else null)
			if b_type != "spectator":
				valid_balls.append(b)

		if valid_balls.size() < 2:
			return

		var juggernauts = [valid_balls[0], valid_balls[1]]
		var hunters = valid_balls.slice(2, valid_balls.size())

		for b in juggernauts:
			_make_juggernaut(world, b)

		for b in hunters:
			if typeof(b) == TYPE_DICTIONARY:
				b["team"] = "Hunters"
				if not b.has("base_max_hp"):
					b["base_max_hp"] = float(b.get("max_hp", 100.0))
				b["max_hp"] = b["base_max_hp"] * 0.8
				b["hp"] = b["max_hp"]
			else:
				if "team" in b: b.team = "Hunters"
				if not b.has_meta("base_max_hp"):
					b.set_meta("base_max_hp", float(b.max_hp if "max_hp" in b else 100.0))
				if "max_hp" in b:
					b.max_hp = b.get_meta("base_max_hp") * 0.8
					if "hp" in b:
						b.hp = b.max_hp

	func _make_juggernaut(world, b) -> void:
		if typeof(b) == TYPE_DICTIONARY:
			b["team"] = "Juggernaut"
			if not b.has("base_max_hp"):
				b["base_max_hp"] = float(b.get("max_hp", 100.0))
			b["max_hp"] = b["base_max_hp"] * 5.0
			b["hp"] = b["max_hp"]

			if not b.has("base_damage"):
				b["base_damage"] = float(b.get("damage", 10.0))
			b["damage"] = b["base_damage"] * 1.5

			if not b.has("base_radius"):
				b["base_radius"] = float(b.get("radius", 10.0))
			b["radius"] = b["base_radius"] * 2.0

			if not b.has("base_speed"):
				b["base_speed"] = float(b.get("speed", 100.0))
			b["speed"] = b["base_speed"] * 0.7

			if not b.has("base_mass"):
				b["base_mass"] = float(b.get("mass", 1.0))
			b["mass"] = b["base_mass"] * 3.0
		else:
			if "team" in b: b.team = "Juggernaut"

			if not b.has_meta("base_max_hp"):
				b.set_meta("base_max_hp", float(b.max_hp if "max_hp" in b else 100.0))
			if "max_hp" in b:
				b.max_hp = b.get_meta("base_max_hp") * 5.0
				if "hp" in b: b.hp = b.max_hp

			if not b.has_meta("base_damage"):
				b.set_meta("base_damage", float(b.damage if "damage" in b else 10.0))
			if "damage" in b:
				b.damage = b.get_meta("base_damage") * 1.5

			if not b.has_meta("base_radius"):
				b.set_meta("base_radius", float(b.radius if "radius" in b else 10.0))
			if "radius" in b:
				b.radius = b.get_meta("base_radius") * 2.0

			if not b.has_meta("base_speed"):
				b.set_meta("base_speed", float(b.speed if "speed" in b else 100.0))
			if "speed" in b:
				b.speed = b.get_meta("base_speed") * 0.7

			if not b.has_meta("base_mass"):
				b.set_meta("base_mass", float(b.mass if "mass" in b else 1.0))
			if "mass" in b:
				b.mass = b.get_meta("base_mass") * 3.0

	func tick(world, balls: Array, delta: float = 0.016) -> void:
		super.tick(world, balls, delta)

		for altar in altars:
			var teams_present = {}
			for b in balls:
				var is_alive = false
				if typeof(b) == TYPE_DICTIONARY:
					is_alive = b.get("alive", false)
				else:
					is_alive = b.get("alive") if "alive" in b else false

				if is_alive and (b.get("ball_type", "") if typeof(b) == TYPE_DICTIONARY else b.get("ball_type") if "ball_type" in b else "") != "spectator":
					var bx = b.get("x", 0.0) if typeof(b) == TYPE_DICTIONARY else b.get("x") if "x" in b else 0.0
					var by = b.get("y", 0.0) if typeof(b) == TYPE_DICTIONARY else b.get("y") if "y" in b else 0.0
					var dist_sq = pow(bx - altar["x"], 2) + pow(by - altar["y"], 2)
					if dist_sq <= pow(altar["radius"], 2):
						var team = b.get("team", b.get("ball_type", "")) if typeof(b) == TYPE_DICTIONARY else b.get("team") if "team" in b else b.get("ball_type") if "ball_type" in b else ""
						if teams_present.has(team):
							teams_present[team] += 1
						else:
							teams_present[team] = 1

						var has_neg = false
						if typeof(b) == TYPE_DICTIONARY and b.has("inventory") and b["inventory"].has("negative_modifier"):
							has_neg = true
							b["inventory"].erase("negative_modifier")
						elif typeof(b) != TYPE_DICTIONARY and "inventory" in b and typeof(b.inventory) == TYPE_ARRAY and b.inventory.has("negative_modifier"):
							has_neg = true
							b.inventory.erase("negative_modifier")

						if has_neg:
							altar["sabotaged_by"] = team
							if world != null and world.has_method("add_event"):
								world.add_event("altar_sabotaged", {"team": team})

						var saboteur = altar.get("sabotaged_by")
						if saboteur != null and saboteur != team:
							var cur_hp = b.get("hp", 100.0) if typeof(b) == TYPE_DICTIONARY else b.get("hp") if "hp" in b else 100.0
							var new_hp = max(0.0, cur_hp - 15.0 * delta)
							if typeof(b) == TYPE_DICTIONARY:
								b["hp"] = new_hp
							else:
								b.hp = new_hp

			if teams_present.size() > 0:
				var max_team = ""
				var max_count = 0
				for t in teams_present.keys():
					if teams_present[t] > max_count:
						max_count = teams_present[t]
						max_team = t
				var tie = 0
				for t in teams_present.keys():
					if teams_present[t] == max_count:
						tie += 1

				if tie == 1:
					if altar["owner"] == max_team:
						altar["capture_progress"] = min(100.0, altar["capture_progress"] + 20.0 * delta)
					else:
						altar["capture_progress"] -= 20.0 * delta
						if altar["capture_progress"] <= 0:
							altar["owner"] = max_team
							altar["capture_progress"] = 0.0
							weather_timer = 0.0
							var ctype = max_team
							if ctype == "fire_elemental" or ctype == "fire_mage" or ctype == "inferno_boss":
								weather = "heatwave"
							elif ctype == "water_elemental" or ctype == "druid" or ctype == "leviathan":
								weather = "heavy_rain"
							elif ctype == "earth_elemental" or ctype == "golem":
								weather = "sandstorm"
							elif ctype == "air_elemental" or ctype == "scout":
								weather = "hurricane"
							elif ctype == "ice_elemental" or ctype == "frost_mage" or ctype == "yeti":
								weather = "blizzard"
							elif ctype == "necro" or ctype == "vampire":
								weather = "blood_moon"
							elif ctype == "paladin" or ctype == "light_mage":
								weather = "solar_flare"
							else:
								var rng = RandomNumberGenerator.new()
								if world != null and "tick_timer" in world:
									rng.seed = int(world.tick_timer * 1000)
								var weathers = ["thunderstorm", "blizzard", "hurricane", "storm", "heatwave", "sandstorm", "heavy_rain"]
								weather = weathers[rng.randi_range(0, weathers.size() - 1)]

							if world != null and ("arena" in world) and world.arena != null:
								if typeof(world.arena) == TYPE_DICTIONARY:
									world.arena["weather"] = weather
								else:
									world.arena.weather = weather

		var boosters = []
		if world != null:
			if typeof(world) == TYPE_DICTIONARY:
				if not world.has("boosters"):
					world["boosters"] = []
				boosters = world["boosters"]
			elif typeof(world) == TYPE_OBJECT:
				if "boosters" in world:
					boosters = world.boosters
				elif world.has_method("has_meta") and world.has_meta("boosters"):
					boosters = world.get_meta("boosters")

		var alive_juggernauts = []
		var dead_juggernauts = []

		for b in balls:
			var team = b.get("team") if typeof(b) == TYPE_DICTIONARY else (b.team if "team" in b else null)
			if team == "Juggernaut":
				var alive = b.get("alive", false) if typeof(b) == TYPE_DICTIONARY else (b.alive if "alive" in b else false)
				if alive:
					alive_juggernauts.append(b)
				else:
					dead_juggernauts.append(b)

		for b in dead_juggernauts:
			var dropped_heal = b.get("dropped_heal", false) if typeof(b) == TYPE_DICTIONARY else (b.get_meta("dropped_heal") if b.has_method("has_meta") and b.has_meta("dropped_heal") else false)
			if not dropped_heal:
				if typeof(b) == TYPE_DICTIONARY:
					b["dropped_heal"] = true
				else:
					if b.has_method("set_meta"):
						b.set_meta("dropped_heal", true)

				var x = b.get("x", 0.0) if typeof(b) == TYPE_DICTIONARY else (b.x if "x" in b else 0.0)
				var y = b.get("y", 0.0) if typeof(b) == TYPE_DICTIONARY else (b.y if "y" in b else 0.0)

				boosters.append({
					"type": "massive_heal",
					"x": x,
					"y": y,
					"value": 500.0
				})
				if world != null and world.has_method("add_event"):
					world.add_event("juggernaut_death", {"message": "A Juggernaut has fallen and dropped a massive heal!"})

		if alive_juggernauts.size() == 1 and dead_juggernauts.size() >= 1:
			var survivor = alive_juggernauts[0]
			var enraged = survivor.get("enraged", false) if typeof(survivor) == TYPE_DICTIONARY else (survivor.get_meta("enraged") if survivor.has_method("has_meta") and survivor.has_meta("enraged") else false)

			if not enraged:
				if typeof(survivor) == TYPE_DICTIONARY:
					survivor["enraged"] = true
					survivor["damage"] = survivor.get("base_damage", 10.0) * 3.0
					survivor["speed"] = survivor.get("base_speed", 100.0) * 1.2
					survivor["radius"] = survivor.get("base_radius", 10.0) * 2.5
				else:
					if survivor.has_method("set_meta"):
						survivor.set_meta("enraged", true)
					if "damage" in survivor:
						var bd = survivor.get_meta("base_damage") if survivor.has_method("has_meta") and survivor.has_meta("base_damage") else 10.0
						survivor.damage = bd * 3.0
					if "speed" in survivor:
						var bs = survivor.get_meta("base_speed") if survivor.has_method("has_meta") and survivor.has_meta("base_speed") else 100.0
						survivor.speed = bs * 1.2
					if "radius" in survivor:
						var br = survivor.get_meta("base_radius") if survivor.has_method("has_meta") and survivor.has_meta("base_radius") else 10.0
						survivor.radius = br * 2.5

				if world != null and world.has_method("add_event"):
					world.add_event("juggernaut_enrage", {"message": "The remaining Juggernaut is enraged!"})

		for b in alive_juggernauts:
			if typeof(b) == TYPE_DICTIONARY:
				if b.has("hp") and b.has("max_hp"):
					b["hp"] = min(b["hp"] + 5.0 * delta, b["max_hp"])
			else:
				if "hp" in b and "max_hp" in b:
					b.hp = min(b.hp + 5.0 * delta, b.max_hp)

	func check_winner(world, balls: Array):
		var alive = []
		for b in balls:
			var is_alive = b.get("alive", false) if typeof(b) == TYPE_DICTIONARY else (b.alive if "alive" in b else false)
			var b_type = b.get("ball_type") if typeof(b) == TYPE_DICTIONARY else (b.ball_type if "ball_type" in b else null)
			if is_alive and b_type != "spectator" and b_type != "shadow_monster":
				alive.append(b)

		if alive.size() == 0:
			return "Draw"

		var juggernaut_alive = false
		var hunters_alive = false

		for b in alive:
			var team = b.get("team") if typeof(b) == TYPE_DICTIONARY else (b.team if "team" in b else null)
			if team == "Juggernaut":
				juggernaut_alive = true
			elif team == "Hunters":
				hunters_alive = true

		if not juggernaut_alive:
			return "Hunters"
		if not hunters_alive:
			return "Juggernaut"

		return null
