extends "res://src/ai/game_modes.gd".GameMode

var tick_timer: float = 0.0
var generation: int = 1
var user_ball_id = null
var learning_rate: float = 0.01

func _init() -> void:
	name = "Interactive Training"
	description = "Train neural network balls by interacting with them. Your actions shape their strategy."

func setup(world, balls: Array) -> void:
	if not "dead_balls" in world:
		world.dead_balls = []

	if balls.size() > 0:
		user_ball_id = balls[0].get("id")

	for b in balls:
		if b.ball_type != "spectator":
			if b.get("id") == user_ball_id:
				b.team = "User"
				if b.has_method("set_meta"):
					b.set_meta("is_user", true)
			else:
				b.ball_type = "neural"
				b.team = "Learning"
				if b.has_method("set_meta"):
					b.set_meta("interactive_fitness", 0.0)

func tick(world, balls: Array, delta: float = 0.016) -> void:
	if not "dead_balls" in world:
		world.dead_balls = []

	tick_timer += delta

	var user_ball = null
	for b in balls:
		if b.get("id") == user_ball_id and b.alive:
			user_ball = b
			break

	for b in balls:
		if not b.alive:
			if not world.dead_balls.has(b):
				if b.has_method("set_meta"):
					b.set_meta("time_since_death", 0.0)
				world.dead_balls.append(b)
			else:
				if b.has_method("get_meta") and b.has_meta("time_since_death"):
					b.set_meta("time_since_death", b.get_meta("time_since_death") + delta)
			continue

		if b.get("team") == "Learning" and user_ball != null:
			var dist_sq = (b.x - user_ball.x) * (b.x - user_ball.x) + (b.y - user_ball.y) * (b.y - user_ball.y)
			var dist = sqrt(dist_sq)
			var p_rad = 300.0
			if "perception_radius" in user_ball: p_rad = float(user_ball.perception_radius)

			if dist < p_rad:
				var fit = b.get_meta("interactive_fitness") if b.has_meta("interactive_fitness") else 0.0
				b.set_meta("interactive_fitness", fit + 1.0 * delta)

			if "hp" in b and "max_hp" in b:
				if b.hp < b.max_hp * 0.2:
					var fit = b.get_meta("interactive_fitness") if b.has_meta("interactive_fitness") else 0.0
					b.set_meta("interactive_fitness", fit - 0.5 * delta)

			if b.has_meta("damage_dealt"):
				var dmg = b.get_meta("damage_dealt")
				if dmg > 0:
					var fit = b.get_meta("interactive_fitness") if b.has_meta("interactive_fitness") else 0.0
					b.set_meta("interactive_fitness", fit + dmg * 2.0 * delta)

	if tick_timer > 30.0:
		tick_timer = 0.0
		generation += 1

func check_winner(world, balls: Array):
	var alive = []
	for b in balls:
		if b.alive and b.ball_type != "spectator":
			alive.append(b)

	if alive.size() == 0:
		return "Draw"

	var teams_alive = {}
	for b in alive:
		var t = b.get("team")
		if t == null: t = b.ball_type
		teams_alive[t] = true

	if teams_alive.size() == 1:
		return teams_alive.keys()[0]

	return null
