extends "res://src/ai/game_modes.gd".GameMode

var coins = []
var time_limit = 120.0
var coin_spawn_timer = 0.0
var coin_spawn_interval = 2.0
var max_coins = 20

func _init().():
	name = "Gold Rush"
	description = "Gold coins randomly spawn across the arena. The more coins you collect, the larger and slower you get. The player with the most coins at the end of the time limit wins."

func tick(world, balls: Array, delta: float = 0.016) -> void:
	.tick(world, balls, delta)

	time_limit -= delta

	var arena_w = 800.0
	var arena_h = 600.0

	if world != null and typeof(world) == TYPE_DICTIONARY and world.has("arena") and world["arena"] != null:
		if typeof(world["arena"]) == TYPE_DICTIONARY:
			if world["arena"].has("width"): arena_w = world["arena"]["width"]
			if world["arena"].has("height"): arena_h = world["arena"]["height"]
		elif typeof(world["arena"]) == TYPE_OBJECT:
			if "width" in world["arena"]: arena_w = world["arena"].width
			if "height" in world["arena"]: arena_h = world["arena"].height

	coin_spawn_timer += delta
	if coin_spawn_timer >= coin_spawn_interval and coins.size() < max_coins:
		coin_spawn_timer -= coin_spawn_interval

		var coin = {
			"id": "gold_coin_" + str(randi() % 90000 + 10000),
			"x": randf() * (arena_w - 100) + 50,
			"y": randf() * (arena_h - 100) + 50,
			"radius": 15.0
		}
		coins.append(coin)

		if world != null and typeof(world) == TYPE_DICTIONARY and world.has("events") and typeof(world["events"]) == TYPE_ARRAY:
			world["events"].append({"type": "coin_spawn", "data": {"x": coin.x, "y": coin.y}})

	for b in balls:
		if typeof(b) == TYPE_DICTIONARY:
			if not b.has("collected_coins"):
				b["collected_coins"] = 0
				b["base_radius"] = b.get("radius", 15.0)
				b["base_speed"] = b.get("speed", 100.0)
		else:
			if not b.has_meta("collected_coins"):
				b.set_meta("collected_coins", 0)
				b.set_meta("base_radius", b.get("radius", 15.0) if "radius" in b else 15.0)
				b.set_meta("base_speed", b.get("speed", 100.0) if "speed" in b else 100.0)

	var coins_to_remove = []
	for coin in coins:
		for b in balls:
			var is_alive = true
			if typeof(b) == TYPE_DICTIONARY: is_alive = b.get("alive", true)
			else: is_alive = b.alive if "alive" in b else true

			if not is_alive:
				continue

			var bx = 0.0
			var by = 0.0
			var br = 15.0

			if typeof(b) == TYPE_DICTIONARY:
				bx = b.get("x", 0.0)
				by = b.get("y", 0.0)
				br = b.get("radius", 15.0)
			else:
				bx = b.x if "x" in b else 0.0
				by = b.y if "y" in b else 0.0
				br = b.radius if "radius" in b else 15.0

			var dx = bx - coin.x
			var dy = by - coin.y
			var dist = sqrt(dx*dx + dy*dy)

			if dist < br + coin.radius:
				if typeof(b) == TYPE_DICTIONARY:
					b["collected_coins"] += 1
					var base_r = b.get("base_radius", 15.0)
					var base_s = b.get("base_speed", 100.0)
					b["radius"] = base_r + (b["collected_coins"] * 2.0)
					b["speed"] = maxf(20.0, base_s - (b["collected_coins"] * 2.0))

					if world != null and typeof(world) == TYPE_DICTIONARY and world.has("events") and typeof(world["events"]) == TYPE_ARRAY:
						world["events"].append({"type": "coin_collected", "data": {"ball_id": b.get("id"), "coins": b["collected_coins"]}})
				else:
					var c_coins = b.get_meta("collected_coins") + 1
					b.set_meta("collected_coins", c_coins)
					var base_r = b.get_meta("base_radius")
					var base_s = b.get_meta("base_speed")

					if "radius" in b: b.radius = base_r + (c_coins * 2.0)
					if "speed" in b: b.speed = maxf(20.0, base_s - (c_coins * 2.0))

					if world != null and typeof(world) == TYPE_DICTIONARY and world.has("events") and typeof(world["events"]) == TYPE_ARRAY:
						world["events"].append({"type": "coin_collected", "data": {"ball_id": b.id if "id" in b else null, "coins": c_coins}})

				coins_to_remove.append(coin)
				break

	var new_coins = []
	for coin in coins:
		if not (coin in coins_to_remove):
			new_coins.append(coin)
	coins = new_coins

func check_winner(world, balls: Array):
	if time_limit <= 0:
		if balls.size() == 0:
			return null

		var alive_balls = []
		for b in balls:
			var is_alive = true
			if typeof(b) == TYPE_DICTIONARY: is_alive = b.get("alive", true)
			else: is_alive = b.alive if "alive" in b else true
			if is_alive:
				alive_balls.append(b)

		if alive_balls.size() == 0:
			return null

		var winner = alive_balls[0]
		var max_coins = -1

		for b in alive_balls:
			var c = 0
			if typeof(b) == TYPE_DICTIONARY: c = b.get("collected_coins", 0)
			else: c = b.get_meta("collected_coins") if b.has_meta("collected_coins") else 0

			if c > max_coins:
				max_coins = c
				winner = b

		if typeof(winner) == TYPE_DICTIONARY:
			if winner.has("team") and winner.team != null and winner.team != "":
				return winner.team
			return winner.get("id", "Unknown")
		else:
			if "team" in winner and winner.team != null and winner.team != "":
				return winner.team
			return winner.id if "id" in winner else "Unknown"
	return null
