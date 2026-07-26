extends "res://src/ai/game_modes.gd"

class CaptureTheFlagElementsInBattleRoyaleMode extends GameMode:
	var center_zone = {"x": 500.0, "y": 500.0, "radius": 150.0}
	var neutral_zones = []
	var boosted_players = {}

	func _init() -> void:
		name = "Capture The Flag Elements in Battle Royale"
		description = "Spawn flags in neutral capture zones. If a player captures the flag and brings it to the center zone, they gain massive stat boosts for the duration of the match."

	func setup(world, balls: Array) -> void:
		super.setup(world, balls)

		var arena_w = 1000.0
		var arena_h = 1000.0
		if world != null:
			if typeof(world) == TYPE_DICTIONARY and world.has("arena"):
				var arena = world["arena"]
				if typeof(arena) == TYPE_DICTIONARY:
					arena_w = arena.get("width", 1000.0)
					arena_h = arena.get("height", 1000.0)
				elif arena != null:
					arena_w = arena.width if "width" in arena else 1000.0
					arena_h = arena.height if "height" in arena else 1000.0
			elif typeof(world) != TYPE_DICTIONARY and "arena" in world and world.arena != null:
				if typeof(world.arena) == TYPE_DICTIONARY:
					arena_w = world.arena.get("width", 1000.0)
					arena_h = world.arena.get("height", 1000.0)
				else:
					arena_w = world.arena.width if "width" in world.arena else 1000.0
					arena_h = world.arena.height if "height" in world.arena else 1000.0

		center_zone = {"x": arena_w / 2.0, "y": arena_h / 2.0, "radius": 100.0}
		neutral_zones = [
			{"x": arena_w * 0.1, "y": arena_h * 0.1, "radius": 50.0},
			{"x": arena_w * 0.9, "y": arena_h * 0.9, "radius": 50.0},
			{"x": arena_w * 0.1, "y": arena_h * 0.9, "radius": 50.0},
			{"x": arena_w * 0.9, "y": arena_h * 0.1, "radius": 50.0}
		]

		var has_boosters = false
		if typeof(world) == TYPE_DICTIONARY:
			if not world.has("boosters"):
				world["boosters"] = []
			has_boosters = true
		elif typeof(world) != TYPE_DICTIONARY and "boosters" in world:
			if world.boosters == null:
				world.boosters = []
			has_boosters = true

		if has_boosters:
			for i in range(neutral_zones.size()):
				var zone = neutral_zones[i]
				var flag = {
					"id": "neutral_flag_" + str(i),
					"x": zone["x"],
					"y": zone["y"],
					"is_flag": true,
					"team": "Neutral",
					"carrier": null,
					"ball_type": "booster"
				}
				if typeof(world) == TYPE_DICTIONARY:
					world["boosters"].append(flag)
				else:
					world.boosters.append(flag)

		boosted_players.clear()

	func tick(world, delta: float) -> void:
		var balls_list = []
		if typeof(world) == TYPE_DICTIONARY and world.has("balls"):
			balls_list = world["balls"]
		elif typeof(world) != TYPE_DICTIONARY and "balls" in world:
			balls_list = world.balls

		var cx = center_zone["x"]
		var cy = center_zone["y"]
		var cr = center_zone["radius"]

		for b in balls_list:
			var is_alive = false
			if typeof(b) == TYPE_DICTIONARY:
				is_alive = b.get("alive", false)
			else:
				is_alive = b.get("alive") if "alive" in b else false

			if not is_alive:
				continue

			var b_id = null
			if typeof(b) == TYPE_DICTIONARY:
				b_id = b.get("id")
			else:
				b_id = b.get("id") if "id" in b else null

			if b_id != null and boosted_players.has(b_id):
				continue

			var bx = 0.0
			var by = 0.0
			var has_flag = false
			if typeof(b) == TYPE_DICTIONARY:
				bx = b.get("x", 0.0)
				by = b.get("y", 0.0)
				has_flag = b.get("has_flag", false)
			else:
				bx = b.get("x") if "x" in b else 0.0
				by = b.get("y") if "y" in b else 0.0
				has_flag = b.get("has_flag") if "has_flag" in b else false

			var dx = bx - cx
			var dy = by - cy
			var dist = sqrt(dx * dx + dy * dy)

			if has_flag and dist <= cr:
				if typeof(b) == TYPE_DICTIONARY:
					b["has_flag"] = false
					var base_s = b.get("base_speed", b.get("speed", 100.0)) * 2.0
					b["base_speed"] = base_s
					b["speed"] = base_s
					var base_d = b.get("base_damage", b.get("damage", 10.0)) * 3.0
					b["base_damage"] = base_d
					b["damage"] = base_d
					var max_h = b.get("max_hp", 100.0) + 500.0
					b["max_hp"] = max_h
					b["hp"] = b.get("hp", 100.0) + 500.0
				else:
					if "has_flag" in b:
						b.has_flag = false
					elif b.has_method("set_meta"):
						b.set_meta("has_flag", false)

					var base_s = b.get("base_speed") if "base_speed" in b else (b.get("speed") if "speed" in b else 100.0)
					base_s *= 2.0
					if "base_speed" in b: b.base_speed = base_s
					if "speed" in b: b.speed = base_s

					var base_d = b.get("base_damage") if "base_damage" in b else (b.get("damage") if "damage" in b else 10.0)
					base_d *= 3.0
					if "base_damage" in b: b.base_damage = base_d
					if "damage" in b: b.damage = base_d

					var cur_hp = b.get("hp") if "hp" in b else 100.0
					var max_h = b.get("max_hp") if "max_hp" in b else 100.0
					max_h += 500.0
					cur_hp += 500.0
					if "hp" in b: b.hp = cur_hp
					if "max_hp" in b: b.max_hp = max_h

				if b_id != null:
					boosted_players[b_id] = true

				if typeof(world) == TYPE_DICTIONARY:
					pass
				elif world.has_method("add_event"):
					world.add_event("flag_captured_center", {"player_id": b_id, "message": "Massive stats boost acquired!"})
