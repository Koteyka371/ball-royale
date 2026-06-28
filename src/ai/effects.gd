class_name Effects

static func apply_weather_effects(ball, weather: String, delta: float, wind_dx: float = 0.0, wind_dy: float = 0.0):
	if not ball.has_meta("base_speed"):
		if "speed" in ball:
			ball.set_meta("base_speed", ball.speed)
		else:
			ball.set_meta("base_speed", 100.0)
	if not ball.has_meta("base_damage"):
		if "damage" in ball:
			ball.set_meta("base_damage", ball.damage)
		else:
			ball.set_meta("base_damage", 10.0)

	var base_spd = ball.get_meta("base_speed")
	var base_dmg = ball.get_meta("base_damage")

	if weather == "clear":
		if "speed" in ball: ball.speed = base_spd
		if "damage" in ball: ball.damage = base_dmg
	elif weather == "rain":
		if "speed" in ball: ball.speed = base_spd * 0.8
		if "damage" in ball: ball.damage = base_dmg
		if "vx" in ball and "vy" in ball:
			ball.x += ball.vx * delta * 0.5
			ball.y += ball.vy * delta * 0.5
	elif weather == "fog":
		if "speed" in ball: ball.speed = base_spd * 0.5
		if "damage" in ball: ball.damage = base_dmg * 0.8
	elif weather == "snow":
		if "speed" in ball: ball.speed = base_spd * 0.5
		if "damage" in ball: ball.damage = base_dmg * 1.2
	elif weather == "wind":
		if "speed" in ball: ball.speed = base_spd
		if "damage" in ball: ball.damage = base_dmg
		ball.x += wind_dx * delta
		ball.y += wind_dy * delta
	elif weather == "thunderstorm":
		if "speed" in ball: ball.speed = base_spd * 1.1
		if "damage" in ball: ball.damage = base_dmg * 1.5
		if randf() < 0.05 * delta:
			if "hp" in ball: ball.hp -= 20
